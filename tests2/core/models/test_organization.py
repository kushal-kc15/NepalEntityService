"""Tests for Organization models in nes2."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from nes2.core.models.base import Name, NameKind
from nes2.core.models.entity import EntitySubType
from nes2.core.models.organization import GovernmentBody, GovernmentType, Organization, PoliticalParty
from nes2.core.models.version import Actor, VersionSummary, VersionType


def test_organization_basic_creation():
    """Test creating a basic Organization entity."""
    
    org = Organization(
        slug="test-organization",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Organization"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/test-organization",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert org.type == "organization"
    assert org.slug == "test-organization"
    assert org.id == "entity:organization/test-organization"


def test_political_party_creation():
    """Test creating a PoliticalParty entity."""
    
    party = PoliticalParty(
        slug="shram-sanskriti-party",
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Shram Sanskriti Party"},
                ne={"full": "श्रम संस्कृति पार्टी"}
            )
        ],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/political_party/shram-sanskriti-party",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert party.type == "organization"
    assert party.sub_type == EntitySubType.POLITICAL_PARTY
    assert party.slug == "shram-sanskriti-party"
    assert party.id == "entity:organization/political_party/shram-sanskriti-party"


def test_political_party_with_attributes():
    """Test PoliticalParty with additional attributes."""
    
    party = PoliticalParty(
        slug="rastriya-swatantra-party",
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Rastriya Swatantra Party"},
                ne={"full": "राष्ट्रिय स्वतन्त्र पार्टी"}
            )
        ],
        attributes={
            "founded": "2022",
            "ideology": "liberal",
            "leader": "Rabi Lamichhane"
        },
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/political_party/rastriya-swatantra-party",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert party.attributes is not None
    assert party.attributes["founded"] == "2022"
    assert party.attributes["ideology"] == "liberal"


def test_government_body_creation():
    """Test creating a GovernmentBody entity."""
    
    gov_body = GovernmentBody(
        slug="election-commission",
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Election Commission of Nepal"},
                ne={"full": "निर्वाचन आयोग"}
            )
        ],
        government_type=GovernmentType.FEDERAL,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/government_body/election-commission",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert gov_body.type == "organization"
    assert gov_body.sub_type == EntitySubType.GOVERNMENT_BODY
    assert gov_body.government_type == GovernmentType.FEDERAL
    assert gov_body.id == "entity:organization/government_body/election-commission"


def test_government_body_types():
    """Test different government body types."""
    
    # Federal government body
    federal_body = GovernmentBody(
        slug="supreme-court",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Supreme Court"})],
        government_type=GovernmentType.FEDERAL,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/government_body/supreme-court",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert federal_body.government_type == GovernmentType.FEDERAL
    
    # Provincial government body
    provincial_body = GovernmentBody(
        slug="bagmati-assembly",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Bagmati Provincial Assembly"})],
        government_type=GovernmentType.PROVINCIAL,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/government_body/bagmati-assembly",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert provincial_body.government_type == GovernmentType.PROVINCIAL
    
    # Local government body
    local_body = GovernmentBody(
        slug="kathmandu-municipality",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Kathmandu Municipality"})],
        government_type=GovernmentType.LOCAL,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/government_body/kathmandu-municipality",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert local_body.government_type == GovernmentType.LOCAL


def test_organization_subtype_enforcement():
    """Test that PoliticalParty and GovernmentBody enforce their subtypes."""
    
    # PoliticalParty should have POLITICAL_PARTY subtype
    party = PoliticalParty(
        slug="test-party",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Party"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/political_party/test-party",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert party.sub_type == EntitySubType.POLITICAL_PARTY
    
    # GovernmentBody should have GOVERNMENT_BODY subtype
    gov = GovernmentBody(
        slug="test-gov",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Government"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:organization/government_body/test-gov",
            type=VersionType.ENTITY,
            version_number=1,
            actor=Actor(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert gov.sub_type == EntitySubType.GOVERNMENT_BODY
