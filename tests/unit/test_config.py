from pathlib import Path

import pytest
from pydantic import ValidationError

from ilias_mcp.config import Settings


def test_settings_loads_toml_and_resolves_its_server_controlled_artifact_directory(
    tmp_path: Path,
) -> None:
    """Break caught: relative artifact paths could escape the configured server location."""
    config_path = tmp_path / "ilias-mcp.toml"
    config_path.write_text(
        """
[instance]
id = "stuttgart"
url = "https://ilias3.uni-stuttgart.de"
timezone = "Europe/Berlin"

[cache]
ttl_seconds = 600

[artifacts]
directory = "runtime-artifacts"
retention_hours = 48
max_bytes = 10485760

[requests]
max_per_minute = 12
max_concurrent = 2

[results]
default_limit = 25
max_limit = 75
""".strip(),
        encoding="utf-8",
    )

    settings = Settings.load(config_path)

    assert settings.instance_id.value == "stuttgart"
    assert settings.instance_url == "https://ilias3.uni-stuttgart.de"
    assert settings.timezone == "Europe/Berlin"
    assert settings.cache_ttl_seconds == 600
    assert settings.artifact_directory == (tmp_path / "runtime-artifacts").resolve()
    assert settings.artifact_retention_hours == 48
    assert settings.max_artifact_bytes == 10_485_760
    assert settings.max_requests_per_minute == 12
    assert settings.max_concurrent_requests == 2
    assert settings.default_result_limit == 25
    assert settings.max_result_limit == 75


def test_environment_overrides_toml_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Break caught: operators cannot safely adjust non-secret deployment settings."""
    config_path = tmp_path / "ilias-mcp.toml"
    config_path.write_text(
        """
[cache]
ttl_seconds = 300

[results]
default_limit = 50
max_limit = 100
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("ILIAS_MCP_CACHE_TTL_SECONDS", "900")
    monkeypatch.setenv("ILIAS_MCP_RESULTS_MAX_LIMIT", "80")

    settings = Settings.load(config_path)

    assert settings.cache_ttl_seconds == 900
    assert settings.max_result_limit == 80


def test_settings_defaults_to_the_safe_stuttgart_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Break caught: a fresh installation could use an insecure or unbounded configuration."""
    monkeypatch.chdir(tmp_path)

    settings = Settings.load(None)

    assert settings.instance_id.value == "stuttgart"
    assert settings.instance_url == "https://ilias3.uni-stuttgart.de"
    assert settings.timezone == "Europe/Berlin"
    assert 60 <= settings.cache_ttl_seconds <= 3600
    assert 1 <= settings.artifact_retention_hours <= 24 * 31
    assert 1 <= settings.max_requests_per_minute <= 60
    assert 1 <= settings.max_concurrent_requests <= 4
    assert 1 <= settings.default_result_limit <= settings.max_result_limit <= 100
    assert settings.artifact_directory == (tmp_path / ".ilias-mcp" / "artifacts").resolve()


@pytest.mark.parametrize(
    "url",
    [
        "http://ilias3.uni-stuttgart.de",
        "https://user:password@ilias3.uni-stuttgart.de",
        "https://ilias3.uni-stuttgart.de/login?token=secret",
        "https://localhost",
        "https://127.0.0.1",
    ],
)
def test_settings_rejects_unsafe_instance_urls(tmp_path: Path, url: str) -> None:
    """Break caught: configuration could direct authenticated requests to unsafe endpoints."""
    config_path = tmp_path / "ilias-mcp.toml"
    config_path.write_text(f"[instance]\nurl = {url!r}\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="instance URL"):
        Settings.load(config_path)


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("cache", "ttl_seconds", 59),
        ("artifacts", "retention_hours", 0),
        ("artifacts", "max_bytes", 1_048_575),
        ("requests", "max_per_minute", 61),
        ("requests", "max_concurrent", 5),
        ("results", "max_limit", 101),
    ],
)
def test_settings_rejects_out_of_range_operational_limits(
    tmp_path: Path, section: str, key: str, value: int
) -> None:
    """Break caught: a malformed override can remove resource and access safeguards."""
    config_path = tmp_path / "ilias-mcp.toml"
    config_path.write_text(f"[{section}]\n{key} = {value}\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        Settings.load(config_path)


def test_settings_rejects_a_default_result_limit_above_its_cap(tmp_path: Path) -> None:
    """Break caught: a default list request can exceed the server result cap."""
    config_path = tmp_path / "ilias-mcp.toml"
    config_path.write_text("[results]\ndefault_limit = 75\nmax_limit = 50\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="default result limit"):
        Settings.load(config_path)
