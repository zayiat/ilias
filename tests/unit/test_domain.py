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
        canonical_reference="course:12345",
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


@pytest.mark.parametrize("raw_instance_type", [None, "", "   ", "x" * 129])
def test_unknown_learning_object_requires_a_bounded_nonblank_raw_instance_type(
    raw_instance_type: str | None,
) -> None:
    """Break caught: an unknown object can lose the raw type needed for forward compatibility."""
    with pytest.raises(ValidationError, match="raw_instance_type"):
        LearningObject(
            id=ObjectId.parse("stuttgart:unknown:17"),
            object_type=ObjectType.UNKNOWN,
            raw_instance_type=raw_instance_type,
            title="New object",
            course_id=ObjectId.parse("stuttgart:course:12345"),
            provenance=provenance(),
        )


def test_known_learning_object_keeps_raw_instance_type_optional() -> None:
    """Break caught: conditional unknown-type validation could reject established object types."""
    learning_object = LearningObject(
        id=ObjectId.parse("stuttgart:file:17"),
        object_type=ObjectType.FILE,
        title="Exercise sheet",
        course_id=ObjectId.parse("stuttgart:course:12345"),
        provenance=provenance(),
    )

    assert learning_object.raw_instance_type is None


@pytest.mark.parametrize("timestamp", ["2026-10-31T18:00:00", "2026-10-31", "31/10/2026 18:00"])
def test_upcoming_item_requires_an_offset_aware_iso_timestamp(timestamp: str) -> None:
    with pytest.raises(ValidationError):
        UpcomingItem(
            kind=UpcomingItemKind.CALENDAR_EVENT,
            title="Tutorial",
            timestamp=timestamp,
            provenance=provenance(),
        )


def test_provenance_marks_authored_content_as_untrusted() -> None:
    source = provenance()

    assert source.content_trust is TrustLevel.UNTRUSTED
    assert source.canonical_reference == "course:12345"
    assert source.retrieved_at.tzinfo is not None


def test_artifact_requires_a_sha256_checksum() -> None:
    with pytest.raises(ValidationError, match="checksum"):
        Artifact(
            id="artifact-1",
            media_type="application/pdf",
            byte_size=128,
            checksum="not-a-checksum",
            provenance=provenance(),
            expires_at="2026-08-21T09:15:00+02:00",
        )


def test_course_rejects_an_identity_from_a_different_instance() -> None:
    with pytest.raises(ValidationError, match="provenance"):
        Course(
            id=ObjectId.parse("other:course:12345"),
            title="Software Engineering",
            is_active=True,
            provenance=provenance(),
        )


def test_learning_object_rejects_its_id_from_a_different_instance() -> None:
    with pytest.raises(ValidationError, match="provenance"):
        LearningObject(
            id=ObjectId.parse("other:file:17"),
            object_type=ObjectType.FILE,
            title="Exercise sheet",
            parent_id=ObjectId.parse("stuttgart:folder:7"),
            course_id=ObjectId.parse("stuttgart:course:12345"),
            provenance=provenance(),
        )


@pytest.mark.parametrize(
    ("parent_id", "course_id"),
    [
        (None, ObjectId.parse("other:course:12345")),
        (ObjectId.parse("other:folder:7"), ObjectId.parse("stuttgart:course:12345")),
    ],
)
def test_learning_object_rejects_related_ids_from_a_different_instance(
    parent_id: ObjectId | None, course_id: ObjectId
) -> None:
    with pytest.raises(ValidationError, match="provenance"):
        LearningObject(
            id=ObjectId.parse("stuttgart:file:17"),
            object_type=ObjectType.FILE,
            title="Exercise sheet",
            parent_id=parent_id,
            course_id=course_id,
            provenance=provenance(),
        )


@pytest.mark.parametrize(
    ("course_id", "object_id"),
    [
        (ObjectId.parse("other:course:12345"), None),
        (None, ObjectId.parse("other:file:17")),
    ],
)
def test_upcoming_item_rejects_related_ids_from_a_different_instance(
    course_id: ObjectId | None, object_id: ObjectId | None
) -> None:
    with pytest.raises(ValidationError, match="provenance"):
        UpcomingItem(
            kind=UpcomingItemKind.DEADLINE,
            title="Submit exercise",
            timestamp="2026-10-31T18:00:00+01:00",
            course_id=course_id,
            object_id=object_id,
            provenance=provenance(),
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
