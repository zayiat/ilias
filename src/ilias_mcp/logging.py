"""Structured, stderr-only logging with conservative redaction."""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

REDACTED = "[REDACTED]"
_SAFE_FIELDS = frozenset({"tool", "duration_ms", "status", "error_code", "attempt"})
_STANDARD_LOG_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)


class RedactionFilter(logging.Filter):
    """Remove dynamic message data and redact non-operational log fields."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize a record in place before any handler serializes it."""
        record.msg = REDACTED
        record.args = ()
        for field_name, value in list(record.__dict__.items()):
            if field_name in _STANDARD_LOG_RECORD_FIELDS:
                continue
            if field_name == "object_id":
                record.__dict__[field_name] = _anonymize(value)
            elif field_name in _SAFE_FIELDS:
                record.__dict__[field_name] = value
            else:
                record.__dict__[field_name] = REDACTED
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
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
