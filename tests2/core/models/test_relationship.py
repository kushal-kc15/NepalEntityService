"""Tests for Relationship model in nes2."""

import pytest
from datetime import date, datetime, UTC
from pydantic import ValidationError

from nes2.core.models.relationship import Relationship
from nes2.core.models.version import Actor, VersionSummary, VersionType


def test_relationship_basic_structure():
    """Test basic Relationship model structure."""
    
    relationship = Relationship(
        source_entity_id="entity:person/ram-chandra-poudel",
        target_entity_id="entity:organization/political_party/nepali-congress",
        type="MEMBER_OF",
        version_summary=VersionSummary(
            entity_or_relationship_id="relationship:person/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF",
            type=VersionType.RELATIONSHIP,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert relationship.source_entity_id == "entity:person/ram-chandra-poudel"
    assert relationship.target_entity_id == "entity:organization/political_party/nepali-congress"
    assert relationship.type == "MEMBER_OF"


def test_relationship_with_temporal_data():
    """Test Relationship with start and end dates."""
    
    relationship = Relationship(
        source_entity_id="entity:person/ram-chandra-poudel",
        target_entity_id="entity:organization/political_party/nepali-congress",
        type="MEMBER_OF",
        start_date=date(2000, 1, 1),
        end_date=date(2024, 12, 31),
        version_summary=VersionSummary(
            entity_or_relationship_id="relationship:person/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF",
            type=VersionType.RELATIONSHIP,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert relationship.start_date == date(2000, 1, 1)
    assert relationship.end_date == date(2024, 12, 31)


def test_relationship_computed_id():
    """Test that Relationship.id is computed correctly."""
    
    relationship = Relationship(
        source_entity_id="entity:person/ram-chandra-poudel",
        target_entity_id="entity:organization/political_party/nepali-congress",
        type="MEMBER_OF",
        version_summary=VersionSummary(
            entity_or_relationship_id="relationship:person/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF",
            type=VersionType.RELATIONSHIP,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    expected_id = "relationship:person/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF"
    assert relationship.id == expected_id


def test_relationship_with_attributes(sample_relationship):
    """Test Relationship with custom attributes."""
    
    relationship = Relationship(
        source_entity_id=sample_relationship["source_entity_id"],
        target_entity_id=sample_relationship["target_entity_id"],
        type=sample_relationship["type"],
        start_date=date.fromisoformat(sample_relationship["start_date"]),
        attributes=sample_relationship["attributes"],
        version_summary=VersionSummary(
            entity_or_relationship_id="relationship:person/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF",
            type=VersionType.RELATIONSHIP,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert relationship.attributes["position"] == "President"
