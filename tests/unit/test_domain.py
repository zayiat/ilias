from pathlib import Path

import pytest
from pydantic import ValidationError

from ilias_mcp.domain import (
    Artifact,
    Course,
    InstanceId,
    LearningObject,
    ObjectId,
    ObjectType,
    OpaqueCursor,
    Page,
    Provenance,
    TrustLevel,
    UpcomingItem,
    UpcomingItemKind,
)


def provenance() -> Provenance:
    return Provenance(
        instance_id=InstanceId(value="stuttgart"),
        canonical_url="https://ilias3.uni-stuttgart.de/goto.php?target=crs_12345",
        retrieved_at="2026-08-20T09:15:00+02:00",
    )


def test_object_id_parses_a_namespaced_identity() -> None:
    object_id = ObjectId.parse("stuttgart:course:12345")

    assert object_id.instance_id.value == "stuttgart"
    assert object_id.object_type is ObjectType.COURSE
    assert object_id.value == "12345"
    assert str(object_id) == "stuttgart:course:12345"


@pytest.mark.parametrize(
    "value",
    [
        "stuttgart:unknown-type:12345",
        "Stuttgart:course:12345",
        "stuttgart:course:",
        "stuttgart:course:12:345",
    ],
)
def test_object_id_rejects_malformed_or_unrecognized_object_types(value: str) -> None:
    with pytest.raises(ValueError):
        ObjectId.parse(value)


def test_normalized_values_are_immutable() -> None:
    course = Course(
        id=ObjectId.parse("stuttgart:course:12345"),
        title="Software Engineering",
        is_active=True,
        provenance=provenance(),
    )

    with pytest.raises(ValidationError):
        course.title = "Changed"  # type: ignore[misc]


def test_learning_object_requires_its_declared_object_type_to_match_its_id() -> None:
    with pytest.raises(ValidationError, match="object_type"):
        LearningObject(
            id=ObjectId.parse("stuttgart:file:17"),
            object_type=ObjectType.EXERCISE,
            title="Exercise sheet",
            course_id=ObjectId.parse("stuttgart:course:12345"),
            provenance=provenance(),
        )


def test_upcoming_item_adds_berlin_timezone_to_naive_iso_timestamp() -> None:
    item = UpcomingItem(
        kind=UpcomingItemKind.DEADLINE,
        title="Submit exercise",
        timestamp="2026-10-31T18:00:00",
        course_id=ObjectId.parse("stuttgart:course:12345"),
        provenance=provenance(),
    )

    assert item.timestamp.isoformat() == "2026-10-31T18:00:00+01:00"


def test_upcoming_item_rejects_non_iso_or_date_only_timestamps() -> None:
    with pytest.raises(ValidationError):
        UpcomingItem(
            kind=UpcomingItemKind.CALENDAR_EVENT,
            title="Tutorial",
            timestamp="31/10/2026 18:00",
            provenance=provenance(),
        )


def test_provenance_marks_authored_content_as_untrusted() -> None:
    source = provenance()

    assert source.content_trust is TrustLevel.UNTRUSTED
    assert source.retrieved_at.tzinfo is not None


def test_artifact_requires_a_sha256_checksum() -> None:
    with pytest.raises(ValidationError, match="checksum"):
        Artifact(
            id="artifact-1",
            local_path=Path("C:/artifacts/artifact-1.pdf"),
            media_type="application/pdf",
            byte_size=128,
            checksum="not-a-checksum",
            provenance=provenance(),
            expires_at="2026-08-21T09:15:00+02:00",
        )


def test_page_limits_item_count_and_keeps_cursor_opaque() -> None:
    course = Course(
        id=ObjectId.parse("stuttgart:course:12345"),
        title="Software Engineering",
        is_active=True,
        provenance=provenance(),
    )
    page = Page[Course](items=[course], limit=1, next_cursor=OpaqueCursor(value="nExt_1"))

    assert page.items == (course,)
    assert page.next_cursor == OpaqueCursor(value="nExt_1")
    with pytest.raises(ValidationError):
        Page[Course](items=[course, course], limit=1)
    with pytest.raises(ValidationError):
        Page[Course](items=[], limit=101)
