import pytest

from ilias_mcp.errors import (
    AdapterIncompatibleError,
    AuthenticationRequiredError,
    ContentTooLargeError,
    ErrorCode,
    ExtractionFailedError,
    IliasMcpError,
    IliasUnavailableError,
    InvalidArgumentError,
    InvalidCursorError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitedError,
    UnsupportedContentTypeError,
)


@pytest.mark.parametrize(
    ("error", "code", "retryable"),
    [
        (AuthenticationRequiredError(), ErrorCode.AUTHENTICATION_REQUIRED, False),
        (PermissionDeniedError(), ErrorCode.PERMISSION_DENIED, False),
        (NotFoundError(), ErrorCode.NOT_FOUND, False),
        (InvalidCursorError(), ErrorCode.INVALID_CURSOR, False),
        (AdapterIncompatibleError(), ErrorCode.ADAPTER_INCOMPATIBLE, False),
        (RateLimitedError(), ErrorCode.RATE_LIMITED, True),
        (ContentTooLargeError(), ErrorCode.CONTENT_TOO_LARGE, False),
        (UnsupportedContentTypeError(), ErrorCode.UNSUPPORTED_CONTENT_TYPE, False),
        (ExtractionFailedError(), ErrorCode.EXTRACTION_FAILED, False),
        (IliasUnavailableError(), ErrorCode.ILIAS_UNAVAILABLE, True),
        (InvalidArgumentError(), ErrorCode.INVALID_ARGUMENT, False),
    ],
)
def test_domain_errors_expose_stable_codes_and_retryability(
    error: IliasMcpError, code: ErrorCode, retryable: bool
) -> None:
    assert error.code is code
    assert error.retryable is retryable
    assert error.to_payload() == {"code": code.value, "message": str(error), "retryable": retryable}


def test_authentication_error_default_message_is_transport_neutral() -> None:
    error = AuthenticationRequiredError()

    assert error.to_payload()["message"] == "Authentication is required."
