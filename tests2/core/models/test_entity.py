"""Tests for Entity model in nes2."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError


def test_entity_requires_primary_name():
    """Test that Entity requires at least one PRIMARY name."""
    from nes2.core.models.entity import Entity, EntityType
    from nes2.core.models.base import Name, NameKind
    from nes2.core.models.version import VersionSummary, VersionType, Actor
    
    # Should fail without PRIMARY name
    with pytest.raises(ValidationError, match="PRIMARY"):
        Entity(
            slug="test-entity",
            type=EntityType.PERSON,
            names=[
                Name(kind=NameKind.ALIAS, en={"full": "Alias Name"})
            ],
            version_summary=VersionSummary(
                entity_or_relationship_id="entity:person:test-entity",
                type=VersionType.ENTITY,
                version_number=1,
                actor=Actor(slug="system"),
                change_description="Initial",
                created_at=datetime.now(UTC)
            ),
            created_at=datetime.now(UTC)
        )


def test_entity_with_authentic_nepali_data(sample_nepali_person):
    """Test Entity creation with authentic Nepali politician data."""
    from nes2.core.models.entity import Entity, EntityType, EntitySubType
    from nes2.core.models.base import Name, NameKind
    from nes2.core.models.version import VersionSummary, VersionType, Actor
    
    entity = Entity(
        slug=sample_nepali_person["slug"],
        type=EntityType.PERSON,
        sub_type=EntitySubType.POLITICIAN,
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en=sample_nepali_person["names"][0]["en"],
                ne=sample_nepali_person["names"][0]["ne"]
            )
        ],
        attributes=sample_nepali_person["attributes"],
        version_summary=VersionSummary(
            entity_or_relationship_id=f"entity:person/politician/{sample_nepali_person['slug']}",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial import",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert entity.slug == "ram-chandra-poudel"
    assert entity.type == EntityType.PERSON
    assert entity.names[0].en.full == "Ram Chandra Poudel"
    assert entity.names[0].ne.full == "राम चन्द्र पौडेल"
    assert entity.id == "entity:person/politician/ram-chandra-poudel"


def test_entity_computed_id():
    """Test that Entity.id is computed correctly."""
    from nes2.core.models.entity import Entity, EntityType, EntitySubType
    from nes2.core.models.base import Name, NameKind
    from nes2.core.models.version import VersionSummary, VersionType, Actor
    
    entity = Entity(
        slug="nepali-congress",
        type=EntityType.ORGANIZATION,
        sub_type=EntitySubType.POLITICAL_PARTY,
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
    from nes2.core.models.entity import Entity, EntityType
    from nes2.core.models.base import Name, NameKind
    from nes2.core.models.version import VersionSummary, VersionType, Actor
    
    # Invalid slug (too short)
    with pytest.raises(ValidationError):
        Entity(
            slug="ab",
            type=EntityType.PERSON,
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
        Entity(
            slug="Test-Entity",
            type=EntityType.PERSON,
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
