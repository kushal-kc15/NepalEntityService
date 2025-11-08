"""Tests for Entity model in nes2."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from nes2.core.models.base import Name, NameKind
from nes2.core.models.entity import Entity, ExternalIdentifier, IdentifierScheme
from nes2.core.models.organization import PoliticalParty
from nes2.core.models.person import Person
from nes2.core.models.version import Actor, VersionSummary, VersionType


def test_entity_requires_primary_name():
    """Test that Entity requires at least one PRIMARY name."""
    # Should fail without PRIMARY name
    with pytest.raises(ValidationError, match="PRIMARY"):
        Person(
            slug="test-entity",
            names=[
                Name(kind=NameKind.ALIAS, en={"full": "Alias Name"})
            ],
            version_summary=VersionSummary(
                entity_or_relationship_id="entity:person/test-entity",
                type=VersionType.ENTITY,
                version_number=1,
                actor=Actor(slug="system"),
                change_description="Initial",
                created_at=datetime.now(UTC)
            ),
            created_at=datetime.now(UTC)
        )


def test_entity_with_multilingual_names():
    """Test Entity with both English and Nepali names."""
    entity = Person(
        slug="test-entity",
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Test Person", "first": "Test", "last": "Person"},
                ne={"full": "परीक्षण व्यक्ति"}
            )
        ],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:person/test-entity",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert entity.slug == "test-entity"
    assert entity.type == "person"
    assert entity.sub_type is None
    assert entity.names[0].en.full == "Test Person"
    assert entity.names[0].ne.full == "परीक्षण व्यक्ति"
    assert entity.id == "entity:person/test-entity"


def test_entity_computed_id():
    """Test that Entity.id is computed correctly for organizations."""
    entity = PoliticalParty(
        slug="nepali-congress",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Nepali Congress"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/political_party/nepali-congress",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert entity.id == "entity:organization/political_party/nepali-congress"


def test_entity_slug_validation():
    """Test Entity slug validation."""
    # Invalid slug (too short)
    with pytest.raises(ValidationError):
        Person(
            slug="ab",
            names=[Name(kind=NameKind.PRIMARY, en={"full": "Test"})],
            version_summary=VersionSummary(
                entity_or_relationship_id="entity:person/ab",
                type=VersionType.ENTITY,
                version_number=1,
                actor=Actor(slug="system"),
                change_description="Initial",
                created_at=datetime.now(UTC)
            ),
            created_at=datetime.now(UTC)
        )
    
    # Invalid slug (uppercase)
    with pytest.raises(ValidationError):
        Person(
            slug="Test-Entity",
            names=[Name(kind=NameKind.PRIMARY, en={"full": "Test"})],
            version_summary=VersionSummary(
                entity_or_relationship_id="entity:person/Test-Entity",
                type=VersionType.ENTITY,
                version_number=1,
                actor=Actor(slug="system"),
                change_description="Initial",
                created_at=datetime.now(UTC)
            ),
            created_at=datetime.now(UTC)
        )


def test_entity_with_multiple_names():
    """Test Entity with multiple name variations."""
    entity = Person(
        slug="test-entity",
        names=[
            Name(kind=NameKind.PRIMARY, en={"full": "Primary Name"}),
            Name(kind=NameKind.ALIAS, en={"full": "Alias Name"}),
            Name(kind=NameKind.ALTERNATE, en={"full": "Alternate Name"})
        ],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:person/test-entity",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert len(entity.names) == 3
    assert entity.names[0].kind == NameKind.PRIMARY
    assert entity.names[1].kind == NameKind.ALIAS
    assert entity.names[2].kind == NameKind.ALTERNATE


def test_entity_with_external_identifiers():
    """Test Entity with external identifiers."""
    entity = Person(
        slug="test-entity",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Person"})],
        identifiers=[
            ExternalIdentifier(
                scheme=IdentifierScheme.WIKIPEDIA,
                value="Test_Person",
                url="https://en.wikipedia.org/wiki/Test_Person"
            ),
            ExternalIdentifier(
                scheme=IdentifierScheme.WIKIDATA,
                value="Q12345"
            )
        ],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:person/test-entity",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert len(entity.identifiers) == 2
    assert entity.identifiers[0].scheme == IdentifierScheme.WIKIPEDIA
    assert entity.identifiers[1].scheme == IdentifierScheme.WIKIDATA


def test_entity_with_tags_and_attributes():
    """Test Entity with tags and custom attributes."""
    entity = Person(
        slug="test-entity",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Person"})],
        tags=["politician", "activist", "writer"],
        attributes={
            "role": "politician",
            "party": "test-party",
            "active": True,
            "years_active": 10
        },
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:person/test-entity",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert len(entity.tags) == 3
    assert "politician" in entity.tags
    assert entity.attributes["role"] == "politician"
    assert entity.attributes["active"] is True


def test_entity_cannot_be_instantiated_directly():
    """Test that Entity class cannot be instantiated directly."""
    # Should fail when trying to instantiate Entity directly
    with pytest.raises(ValidationError, match="Cannot instantiate Entity directly"):
        Entity(
            slug="test-person",
            type="person",
            names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Person"})],
            version_summary=VersionSummary(
                entity_or_relationship_id="entity:person/test-person",
                type=VersionType.ENTITY,
                version_number=1,
                actor=Actor(slug="system"),
                change_description="Initial",
                created_at=datetime.now(UTC)
            ),
            created_at=datetime.now(UTC)
        )
