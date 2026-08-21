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
    assert payload["content"] == "[REDACTED]"
    assert all(
        handler.stream is not sys.stdout for handler in logging.getLogger("ilias_mcp").handlers
    )
