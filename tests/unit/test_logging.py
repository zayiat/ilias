import json
import logging
import sys

import pytest

from ilias_mcp.logging import RedactionFilter, configure_logging


@pytest.mark.parametrize(
    "message",
    [
        "Cookie: session=super-secret-cookie",
        "Authorization: Bearer top-secret-token",
        "password=hunter2",
        "csrf_token=csrf-secret",
        "https://ilias3.uni-stuttgart.de/goto.php?token=query-secret&course=42",
    ],
)
def test_redaction_filter_removes_common_sensitive_values(message: str) -> None:
    """Break caught: operational messages can disclose session or credential material."""
    record = logging.LogRecord("ilias_mcp.test", logging.INFO, __file__, 1, message, (), None)

    assert RedactionFilter().filter(record)

    rendered = record.getMessage()
    assert "super-secret-cookie" not in rendered
    assert "top-secret-token" not in rendered
    assert "hunter2" not in rendered
    assert "csrf-secret" not in rendered
    assert "query-secret" not in rendered
    assert "[REDACTED]" in rendered


def test_redaction_filter_removes_authored_content_from_formatted_arguments() -> None:
    """Break caught: titles or document text interpolated into a log message can leak content."""
    authored_content = "Private lecture notes: do not redistribute"
    record = logging.LogRecord(
        "ilias_mcp.test", logging.INFO, __file__, 1, "Fetched object: %s", (authored_content,), None
    )

    assert RedactionFilter().filter(record)

    assert authored_content not in record.getMessage()
    assert "[REDACTED]" in record.getMessage()


def test_configure_logging_emits_structured_redacted_logs_to_stderr_only(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Break caught: runtime logs can corrupt stdout protocol traffic or expose content."""
    configure_logging("INFO")
    logger = logging.getLogger("ilias_mcp.runtime")
    logger.info(
        "completed request",
        extra={
            "tool": "list_courses",
            "duration_ms": 12,
            "status": "ok",
            "object_id": "stuttgart:course:12345",
            "content": "Private course material",
        },
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.err)

    assert captured.out == ""
    assert payload["tool"] == "list_courses"
    assert payload["duration_ms"] == 12
    assert payload["status"] == "ok"
    assert payload["object_id"].startswith("sha256:")
    assert "12345" not in captured.err
    assert "Private course material" not in captured.err
    assert "content" not in payload
    assert all(
        handler.stream is not sys.stdout for handler in logging.getLogger("ilias_mcp").handlers
    )


def test_stderr_logging_pipeline_redacts_sensitive_values_from_all_output_slots(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Break caught: secret or authored values can bypass redaction through structured fields."""
    values = {
        "cookie": "cookie-1f7c8b",
        "authorization": "Bearer auth-2d8e9f",
        "password": "password-3a4b5c",
        "csrf": "csrf-4d5e6f",
        "session": "session-5a6b7c",
        "access_token": "access-6b7c8d",
        "api_token": "api-7c8d9e",
        "query": "query-8d9e0f",
        "content": "authored-9e0f1a",
        "logger_name": "hunter2",
        "field_name": "api_token_secret123",
    }
    configure_logging("INFO")
    logger = logging.getLogger(f"ilias_mcp.{values['logger_name']}")
    logger.info(
        "Cookie=%(cookie)s Authorization=%(authorization)s password=%(password)s "
        "csrf=%(csrf)s session=%(session)s access_token=%(access_token)s "
        "api_token=%(api_token)s https://example.invalid/?token=%(query)s %(content)s",
        values,
        extra={
            "tool": values["access_token"],
            "duration_ms": values["api_token"],
            "status": values["content"],
            "error_code": values["authorization"],
            "attempt": values["session"],
            "object_id": values["csrf"],
            "content": values["content"],
            values["field_name"]: values["api_token"],
        },
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.err)

    assert captured.out == ""
    for value in values.values():
        assert value not in captured.err
        assert value.split("-", maxsplit=1)[0] not in captured.err
    assert payload["tool"] == "[REDACTED]"
    assert payload["duration_ms"] == "[REDACTED]"
    assert payload["status"] == "[REDACTED]"
    assert payload["error_code"] == "[REDACTED]"
    assert payload["attempt"] == "[REDACTED]"
    assert payload["object_id"] == "[REDACTED]"
    assert "content" not in payload
    assert values["field_name"] not in payload
    assert payload["logger"] == "ilias_mcp"


def test_stderr_logging_pipeline_keeps_valid_operational_metadata(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Break caught: safe redaction removes the structured data needed for operations."""
    configure_logging("INFO")
    logging.getLogger("ilias_mcp.runtime").info(
        "completed request",
        extra={
            "tool": "list_courses",
            "duration_ms": 12,
            "status": "ok",
            "error_code": "RATE_LIMITED",
            "attempt": 1,
            "object_id": "stuttgart:course:12345",
        },
    )

    payload = json.loads(capsys.readouterr().err)

    assert payload["logger"] == "ilias_mcp"
    assert payload["tool"] == "list_courses"
    assert payload["duration_ms"] == 12
    assert payload["status"] == "ok"
    assert payload["error_code"] == "RATE_LIMITED"
    assert payload["attempt"] == 1
    assert payload["object_id"].startswith("sha256:")


def test_stderr_logging_pipeline_redacts_nonprimitive_nominally_safe_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Break caught: malformed structured values raise or bypass the redaction filter."""
    configure_logging("INFO")
    logging.getLogger("ilias_mcp.runtime").info(
        "completed request",
        extra={
            "tool": ["authored-value"],
            "duration_ms": 1.5,
            "status": {"authored-value"},
            "error_code": ["AUTHENTICATION_REQUIRED"],
            "attempt": True,
        },
    )

    payload = json.loads(capsys.readouterr().err)

    assert payload["tool"] == "[REDACTED]"
    assert payload["duration_ms"] == "[REDACTED]"
    assert payload["status"] == "[REDACTED]"
    assert payload["error_code"] == "[REDACTED]"
    assert payload["attempt"] == "[REDACTED]"
