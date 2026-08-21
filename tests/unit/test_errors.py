import pytest

from ilias_mcp.errors import (
    AdapterIncompatibleError,
    AuthenticationRequiredError,
    ErrorCode,
    IliasMcpError,
    IliasUnavailableError,
    InvalidCursorError,
    RateLimitedError,
)


@pytest.mark.parametrize(
    ("error", "code", "retryable"),
    [
        (AuthenticationRequiredError(), ErrorCode.AUTHENTICATION_REQUIRED, False),
        (InvalidCursorError(), ErrorCode.INVALID_CURSOR, False),
        (AdapterIncompatibleError(), ErrorCode.ADAPTER_INCOMPATIBLE, False),
        (RateLimitedError(), ErrorCode.RATE_LIMITED, True),
        (IliasUnavailableError(), ErrorCode.ILIAS_UNAVAILABLE, True),
    ],
)
def test_domain_errors_expose_stable_codes_and_retryability(
    error: IliasMcpError, code: ErrorCode, retryable: bool
) -> None:
    assert error.code is code
    assert error.retryable is retryable
    assert error.to_payload() == {"code": code.value, "message": str(error), "retryable": retryable}


def test_error_payload_does_not_require_transport_specific_fields() -> None:
    error = AuthenticationRequiredError("Run ilias-mcp auth login.")

    assert error.to_payload()["message"] == "Run ilias-mcp auth login."
