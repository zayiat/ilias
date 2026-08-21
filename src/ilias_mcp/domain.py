"""Immutable, normalized values shared across ILIAS MCP layers."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DEFAULT_PAGE_LIMIT = 50
MAX_PAGE_LIMIT = 100


class DomainModel(BaseModel):
    """Base model that prevents mutation and unknown transport-specific fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class InstanceId(DomainModel):
    """A stable, normalized identifier for an ILIAS installation."""

    value: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("instance ID must be a string")
        return value.strip()

    def __str__(self) -> str:
        return self.value


class ObjectType(StrEnum):
    """Normalized ILIAS object types exposed by the initial domain."""

    COURSE = "course"
    FOLDER = "folder"
    FILE = "file"
    EXERCISE = "exercise"
    FORUM = "forum"
    TEST = "test"
    SURVEY = "survey"
    GROUP = "group"
    LEARNING_MODULE = "learning_module"
    UNKNOWN = "unknown"


class ObjectId(DomainModel):
    """An object identity stable only within its instance and object type."""

    instance_id: InstanceId
    object_type: ObjectType
    value: str = Field(pattern=r"^[1-9][0-9]*$")

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("object ID value must be a string")
        return value.strip()

    @classmethod
    def parse(cls, value: str) -> ObjectId:
        """Parse the externally exposed ``instance:type:value`` form."""
        if not isinstance(value, str):
            raise ValueError("object ID must be a string")
        parts = value.split(":")
        if len(parts) != 3:
            raise ValueError("object ID must use instance:type:value format")
        return cls(
            instance_id=InstanceId(value=parts[0]),
            object_type=ObjectType(parts[1]),
            value=parts[2],
        )

    def __str__(self) -> str:
        return f"{self.instance_id}:{self.object_type.value}:{self.value}"


class OpaqueCursor(DomainModel):
    """A caller-visible cursor whose internal representation is not interpreted."""

    value: str = Field(min_length=1, max_length=1024)

    @field_validator("value")
    @classmethod
    def reject_blank_value(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("cursor cannot be blank")
        return value


class TrustLevel(StrEnum):
    """Trust classification for authored content returned by the server."""

    UNTRUSTED = "untrusted"


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        timestamp = value
    elif isinstance(value, str) and "T" in value:
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError("timestamp must be ISO 8601") from error
    else:
        raise ValueError("timestamp must be an ISO 8601 datetime")

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must include an explicit timezone offset")
    return timestamp


class Provenance(DomainModel):
    """Source and trust context for content or metadata visible to a client."""

    instance_id: InstanceId
    canonical_reference: str = Field(min_length=1, max_length=2048)
    retrieved_at: datetime
    content_trust: TrustLevel = TrustLevel.UNTRUSTED

    @field_validator("canonical_reference")
    @classmethod
    def reject_blank_canonical_reference(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("canonical reference cannot be blank")
        return value

    @field_validator("retrieved_at", mode="before")
    @classmethod
    def normalize_retrieved_at(cls, value: Any) -> datetime:
        return _parse_timestamp(value)


class Course(DomainModel):
    """An enrolled ILIAS course with a normalized identity."""

    id: ObjectId
    title: str = Field(min_length=1)
    is_active: bool
    description: str | None = None
    provenance: Provenance

    @model_validator(mode="after")
    def require_course_identity(self) -> Course:
        if self.id.object_type is not ObjectType.COURSE:
            raise ValueError("course ID must have object type course")
        _ensure_instance_cohesion(self.provenance, self.id)
        return self


class LearningObject(DomainModel):
    """A typed item that is visible in a course hierarchy."""

    id: ObjectId
    object_type: ObjectType
    title: str = Field(min_length=1)
    description: str | None = None
    parent_id: ObjectId | None = None
    course_id: ObjectId
    canonical_reference: str | None = None
    is_available: bool = True
    has_children: bool = False
    provenance: Provenance
    raw_instance_type: str | None = None

    @model_validator(mode="after")
    def validate_identity_types(self) -> LearningObject:
        if self.id.object_type is not self.object_type:
            raise ValueError("object_type must match the object ID type")
        if self.course_id.object_type is not ObjectType.COURSE:
            raise ValueError("course_id must have object type course")
        _ensure_instance_cohesion(self.provenance, self.id, self.parent_id, self.course_id)
        return self


class UpcomingItemKind(StrEnum):
    """The only structured sources that can produce upcoming items."""

    DEADLINE = "deadline"
    CALENDAR_EVENT = "calendar_event"


class UpcomingItem(DomainModel):
    """A structured ILIAS deadline or calendar event, never an inferred date."""

    kind: UpcomingItemKind
    title: str = Field(min_length=1)
    timestamp: datetime
    original_display_text: str | None = None
    course_id: ObjectId | None = None
    object_id: ObjectId | None = None
    provenance: Provenance

    @field_validator("timestamp", mode="before")
    @classmethod
    def normalize_timestamp(cls, value: Any) -> datetime:
        return _parse_timestamp(value)

    @model_validator(mode="after")
    def require_course_identity(self) -> UpcomingItem:
        if self.course_id is not None and self.course_id.object_type is not ObjectType.COURSE:
            raise ValueError("course_id must have object type course")
        _ensure_instance_cohesion(self.provenance, self.course_id, self.object_id)
        return self


class Artifact(DomainModel):
    """Metadata for a server-managed local file eligible for extraction."""

    id: str = Field(min_length=1)
    media_type: str = Field(min_length=1)
    byte_size: int = Field(ge=0)
    checksum: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance: Provenance
    expires_at: datetime

    @field_validator("expires_at", mode="before")
    @classmethod
    def normalize_expiry(cls, value: Any) -> datetime:
        return _parse_timestamp(value)


def _ensure_instance_cohesion(provenance: Provenance, *object_ids: ObjectId | None) -> None:
    if any(
        object_id is not None and object_id.instance_id != provenance.instance_id
        for object_id in object_ids
    ):
        raise ValueError("object IDs must match the provenance instance")


class Page[ItemT](DomainModel):
    """A bounded page of normalized values and an optional opaque continuation."""

    items: tuple[ItemT, ...]
    limit: int = Field(default=DEFAULT_PAGE_LIMIT, ge=1, le=MAX_PAGE_LIMIT)
    next_cursor: OpaqueCursor | None = None

    @model_validator(mode="after")
    def enforce_item_bound(self) -> Page[ItemT]:
        if len(self.items) > self.limit:
            raise ValueError("page contains more items than its limit")
        return self
