"""Tests for Version model in nes2."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from nes2.core.models.version import Actor, Version, VersionSummary, VersionType


def test_version_summary_structure():
    """Test VersionSummary model structure."""
    
    version_summary = VersionSummary(
        entity_or_relationship_id="entity:person/ram-chandra-poudel",
        type=VersionType.ENTITY,
        version_number=1,
        actor=Actor(slug="system"),
        change_description="Initial import",
        created_at=datetime.now(UTC)
    )
    
    assert version_summary.entity_or_relationship_id == "entity:person/ram-chandra-poudel"
    assert version_summary.type == VersionType.ENTITY
    assert version_summary.version_number == 1
    assert version_summary.change_description == "Initial import"


def test_version_computed_id():
    """Test that Version.id is computed correctly."""
    
    version_summary = VersionSummary(
        entity_or_relationship_id="entity:person/ram-chandra-poudel",
        type=VersionType.ENTITY,
        version_number=2,
        actor=Actor(slug="system"),
        change_description="Update",
        created_at=datetime.now(UTC)
    )
    
    expected_id = "version:entity:person/ram-chandra-poudel:2"
    assert version_summary.id == expected_id


def test_version_with_snapshot():
    """Test Version model with snapshot data."""
    
    snapshot_data = {
        "slug": "ram-chandra-poudel",
        "type": "person",
        "names": [{"kind": "PRIMARY", "en": {"full": "Ram Chandra Poudel"}}]
    }
    
    version = Version(
        entity_or_relationship_id="entity:person/ram-chandra-poudel",
        type=VersionType.ENTITY,
        version_number=1,
        actor=Actor(slug="system", name="System Importer"),
        change_description="Initial import",
        created_at=datetime.now(UTC),
        snapshot=snapshot_data
    )
    
    assert version.snapshot is not None
    assert version.snapshot["slug"] == "ram-chandra-poudel"
    assert version.actor.name == "System Importer"


def test_actor_model():
    """Test Actor model structure."""
    
    actor = Actor(slug="csv-importer", name="CSV Import System")
    
    assert actor.slug == "csv-importer"
    assert actor.name == "CSV Import System"
    assert actor.id == "actor:csv-importer"
