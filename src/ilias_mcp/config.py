"""Validated, non-secret runtime configuration."""

from __future__ import annotations

import ipaddress
import os
import tomllib
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ilias_mcp.domain import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT, InstanceId

DEFAULT_INSTANCE_URL = "https://ilias3.uni-stuttgart.de"
DEFAULT_TIMEZONE = "Europe/Berlin"
MIN_CACHE_TTL_SECONDS = 60
MAX_CACHE_TTL_SECONDS = 3600
MAX_ARTIFACT_RETENTION_HOURS = 24 * 31
MIN_ARTIFACT_BYTES = 1024 * 1024
MAX_ARTIFACT_BYTES = 100 * 1024 * 1024
MAX_REQUESTS_PER_MINUTE = 60
MAX_CONCURRENT_REQUESTS = 4


class Settings(BaseModel):
    """Non-secret settings loaded from TOML with explicit environment overrides."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    instance_id: InstanceId = Field(default_factory=lambda: InstanceId(value="stuttgart"))
    instance_url: str = DEFAULT_INSTANCE_URL
    timezone: str = DEFAULT_TIMEZONE
    cache_ttl_seconds: int = Field(default=300, ge=MIN_CACHE_TTL_SECONDS, le=MAX_CACHE_TTL_SECONDS)
    artifact_directory: Path = Field(
        default_factory=lambda: (Path.cwd() / ".ilias-mcp" / "artifacts").resolve()
    )
    artifact_retention_hours: int = Field(default=24, ge=1, le=MAX_ARTIFACT_RETENTION_HOURS)
    max_artifact_bytes: int = Field(
        default=25 * 1024 * 1024, ge=MIN_ARTIFACT_BYTES, le=MAX_ARTIFACT_BYTES
    )
    max_requests_per_minute: int = Field(default=20, ge=1, le=MAX_REQUESTS_PER_MINUTE)
    max_concurrent_requests: int = Field(default=2, ge=1, le=MAX_CONCURRENT_REQUESTS)
    default_result_limit: int = Field(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT)
    max_result_limit: int = Field(default=MAX_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT)

    @field_validator("instance_id", mode="before")
    @classmethod
    def parse_instance_id(cls, value: InstanceId | str) -> InstanceId | str:
        """Accept the scalar representation used in TOML and environment settings."""
        if isinstance(value, str):
            return InstanceId(value=value)
        return value

    @field_validator("instance_url")
    @classmethod
    def validate_instance_url(cls, value: str) -> str:
        """Accept only credential-free public HTTPS base URLs."""
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("instance URL must be a credential-free HTTPS base URL")

        hostname = parsed.hostname.lower()
        if hostname == "localhost":
            raise ValueError("instance URL must not target localhost")
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            if not address.is_global:
                raise ValueError("instance URL must not target a non-public IP address")

        return urlunsplit(("https", parsed.netloc, parsed.path.rstrip("/"), "", ""))

    @field_validator("artifact_directory", mode="before")
    @classmethod
    def resolve_artifact_directory(cls, value: str | Path) -> Path:
        """Resolve the directory before later artifact code can use it."""
        return Path(value).expanduser().resolve()

    @model_validator(mode="after")
    def ensure_default_result_limit_is_bounded(self) -> Settings:
        """Keep default list requests within the configured hard cap."""
        if self.default_result_limit > self.max_result_limit:
            raise ValueError("default result limit must not exceed the maximum result limit")
        return self

    @classmethod
    def load(cls, config_path: Path | None) -> Settings:
        """Load non-secret TOML settings and apply explicit environment overrides."""
        base_directory = (config_path.parent if config_path is not None else Path.cwd()).resolve()
        values: dict[str, Any] = {"artifact_directory": base_directory / ".ilias-mcp" / "artifacts"}
        if config_path is not None:
            values.update(_read_toml(config_path, base_directory))
        values.update(_environment_overrides(base_directory))
        return cls.model_validate(values)


def _read_toml(config_path: Path, base_directory: Path) -> dict[str, Any]:
    """Map the supported TOML sections to the flat settings model."""
    with config_path.open("rb") as config_file:
        raw_config = tomllib.load(config_file)
    if not isinstance(raw_config, dict):
        raise ValueError("configuration must be a TOML table")

    section_fields = {
        "instance": {"id": "instance_id", "url": "instance_url", "timezone": "timezone"},
        "cache": {"ttl_seconds": "cache_ttl_seconds"},
        "artifacts": {
            "directory": "artifact_directory",
            "retention_hours": "artifact_retention_hours",
            "max_bytes": "max_artifact_bytes",
        },
        "requests": {
            "max_per_minute": "max_requests_per_minute",
            "max_concurrent": "max_concurrent_requests",
        },
        "results": {"default_limit": "default_result_limit", "max_limit": "max_result_limit"},
    }
    values: dict[str, Any] = {}
    unexpected_sections = set(raw_config) - set(section_fields)
    if unexpected_sections:
        raise ValueError("configuration contains an unsupported section")

    for section, fields in section_fields.items():
        raw_section = raw_config.get(section, {})
        if not isinstance(raw_section, dict):
            raise ValueError(f"configuration section {section!r} must be a table")
        unexpected_fields = set(raw_section) - set(fields)
        if unexpected_fields:
            raise ValueError(f"configuration section {section!r} contains an unsupported setting")
        for toml_key, settings_key in fields.items():
            if toml_key not in raw_section:
                continue
            value = raw_section[toml_key]
            if settings_key == "artifact_directory":
                value = base_directory / Path(value)
            values[settings_key] = value
    return values


def _environment_overrides(base_directory: Path) -> dict[str, str | Path]:
    """Read only documented non-secret override variables."""
    names = {
        "ILIAS_MCP_INSTANCE_ID": "instance_id",
        "ILIAS_MCP_INSTANCE_URL": "instance_url",
        "ILIAS_MCP_TIMEZONE": "timezone",
        "ILIAS_MCP_CACHE_TTL_SECONDS": "cache_ttl_seconds",
        "ILIAS_MCP_ARTIFACT_DIRECTORY": "artifact_directory",
        "ILIAS_MCP_ARTIFACT_RETENTION_HOURS": "artifact_retention_hours",
        "ILIAS_MCP_MAX_ARTIFACT_BYTES": "max_artifact_bytes",
        "ILIAS_MCP_REQUESTS_MAX_PER_MINUTE": "max_requests_per_minute",
        "ILIAS_MCP_REQUESTS_MAX_CONCURRENT": "max_concurrent_requests",
        "ILIAS_MCP_RESULTS_DEFAULT_LIMIT": "default_result_limit",
        "ILIAS_MCP_RESULTS_MAX_LIMIT": "max_result_limit",
    }
    values: dict[str, str | Path] = {}
    for environment_name, settings_name in names.items():
        value = os.environ.get(environment_name)
        if value is None:
            continue
        if settings_name == "artifact_directory":
            values[settings_name] = base_directory / Path(value)
        else:
            values[settings_name] = value
    return values
