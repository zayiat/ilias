"""Stable project failure taxonomy independent of MCP transport details."""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar


class ErrorCode(StrEnum):
    """Project error codes that clients may handle programmatically."""

    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    ADAPTER_INCOMPATIBLE = "ADAPTER_INCOMPATIBLE"
    CONTENT_TOO_LARGE = "CONTENT_TOO_LARGE"
    UNSUPPORTED_CONTENT_TYPE = "UNSUPPORTED_CONTENT_TYPE"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    ILIAS_UNAVAILABLE = "ILIAS_UNAVAILABLE"
    INVALID_CURSOR = "INVALID_CURSOR"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"


class IliasMcpError(Exception):
    """Base error with a stable client-facing code and retryability signal."""

    code: ClassVar[ErrorCode]
    retryable: ClassVar[bool] = False
    default_message: ClassVar[str] = "ILIAS MCP operation failed."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)

    def to_payload(self) -> dict[str, str | bool]:
        """Return transport-neutral fields suitable for a later error mapper."""
        return {"code": self.code.value, "message": self.message, "retryable": self.retryable}


class AuthenticationRequiredError(IliasMcpError):
    code = ErrorCode.AUTHENTICATION_REQUIRED
    default_message = "Authentication is required. Run ilias-mcp auth login."


class PermissionDeniedError(IliasMcpError):
    code = ErrorCode.PERMISSION_DENIED
    default_message = "The authenticated user is not permitted to access this resource."


class NotFoundError(IliasMcpError):
    code = ErrorCode.NOT_FOUND
    default_message = "The requested ILIAS resource was not found."


class RateLimitedError(IliasMcpError):
    code = ErrorCode.RATE_LIMITED
    retryable = True
    default_message = "ILIAS rate-limited this operation."


class AdapterIncompatibleError(IliasMcpError):
    code = ErrorCode.ADAPTER_INCOMPATIBLE
    default_message = "The ILIAS page structure is incompatible with this capability."


class ContentTooLargeError(IliasMcpError):
    code = ErrorCode.CONTENT_TOO_LARGE
    default_message = "The requested content exceeds the configured size limit."


class UnsupportedContentTypeError(IliasMcpError):
    code = ErrorCode.UNSUPPORTED_CONTENT_TYPE
    default_message = "The requested content type is not supported."


class ExtractionFailedError(IliasMcpError):
    code = ErrorCode.EXTRACTION_FAILED
    default_message = "Local document extraction failed."


class IliasUnavailableError(IliasMcpError):
    code = ErrorCode.ILIAS_UNAVAILABLE
    retryable = True
    default_message = "ILIAS is currently unavailable."


class InvalidCursorError(IliasMcpError):
    code = ErrorCode.INVALID_CURSOR
    default_message = "The supplied cursor is invalid."


class InvalidArgumentError(IliasMcpError):
    code = ErrorCode.INVALID_ARGUMENT
    default_message = "A supplied argument is invalid."
