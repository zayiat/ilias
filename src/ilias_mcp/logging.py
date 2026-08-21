"""Structured, stderr-only logging with conservative redaction."""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from ilias_mcp.domain import ObjectId
from ilias_mcp.errors import ErrorCode

REDACTED = "[REDACTED]"
_STANDARD_LOG_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)
_OPERATIONAL_TOOL_NAMES = frozenset(
    {
        "get_auth_status",
        "list_courses",
        "get_course",
        "list_course_objects",
        "get_object",
        "list_upcoming_items",
        "get_dashboard_context",
        "download_file",
        "extract_document_text",
        "refresh_cache",
    }
)
_OPERATIONAL_STATUSES = frozenset({"ok", "error", "started", "cancelled", "rate_limited"})
_ERROR_CODES = frozenset(error_code.value for error_code in ErrorCode)


class RedactionFilter(logging.Filter):
    """Remove dynamic message data and redact non-operational log fields."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize a record in place before any handler serializes it."""
        record.msg = REDACTED
        record.args = ()
        record.name = "ilias_mcp"
        for field_name, value in list(record.__dict__.items()):
            if field_name in _STANDARD_LOG_RECORD_FIELDS:
                continue
            if field_name == "object_id":
                record.__dict__[field_name] = _anonymize(value)
            elif field_name in {"tool", "duration_ms", "status", "error_code", "attempt"}:
                record.__dict__[field_name] = _sanitize_operational_field(field_name, value)
            else:
                del record.__dict__[field_name]
        return True


class _JsonFormatter(logging.Formatter):
    """Serialize the safe operational fields in a stable JSON log line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field_name, value in record.__dict__.items():
            if field_name not in _STANDARD_LOG_RECORD_FIELDS:
                payload[field_name] = value
        return json.dumps(payload, sort_keys=True, default=str)


def configure_logging(level: str) -> None:
    """Configure the package logger with one redacted stderr handler."""
    numeric_level = logging.getLevelName(level.upper())
    if not isinstance(numeric_level, int):
        raise ValueError(f"invalid log level: {level}")

    package_logger = logging.getLogger("ilias_mcp")
    package_logger.setLevel(numeric_level)
    package_logger.propagate = False
    for handler in list(package_logger.handlers):
        package_logger.removeHandler(handler)
        handler.close()

    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(RedactionFilter())
    handler.setFormatter(_JsonFormatter())
    package_logger.addHandler(handler)


def _anonymize(value: object) -> str:
    """Return a deterministic identifier suitable for operational correlation."""
    try:
        ObjectId.parse(str(value))
    except ValueError:
        return REDACTED
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _sanitize_operational_field(field_name: str, value: object) -> object:
    """Preserve only bounded, schema-shaped operational metadata."""
    if field_name == "tool" and isinstance(value, str) and value in _OPERATIONAL_TOOL_NAMES:
        return value
    if field_name == "status" and isinstance(value, str) and value in _OPERATIONAL_STATUSES:
        return value
    if field_name == "error_code" and isinstance(value, str) and value in _ERROR_CODES:
        return value
    if field_name == "duration_ms" and _is_bounded_integer(value, upper_bound=3_600_000):
        return value
    if field_name == "attempt" and _is_bounded_integer(value, upper_bound=100):
        return value
    return REDACTED


def _is_bounded_integer(value: object, upper_bound: int) -> bool:
    """Avoid accepting booleans or arbitrary objects as numeric log fields."""
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= upper_bound
