"""Tests for identifier builders in nes2."""

import pytest


def test_build_entity_id_with_subtype():
    """Test building entity ID with subtype."""
    from nes2.core.identifiers.builders import build_entity_id
    
    entity_id = build_entity_id("person", "politician", "ram-chandra-poudel")
    assert entity_id == "entity:person/politician/ram-chandra-poudel"


def test_build_entity_id_without_subtype():
    """Test building entity ID without subtype."""
    from nes2.core.identifiers.builders import build_entity_id
    
    entity_id = build_entity_id("person", None, "ram-chandra-poudel")
    assert entity_id == "entity:person/ram-chandra-poudel"


def test_break_entity_id_with_subtype():
    """Test breaking entity ID with subtype."""
    from nes2.core.identifiers.builders import break_entity_id
    
    components = break_entity_id("entity:person/politician/ram-chandra-poudel")
    assert components.type == "person"
    assert components.subtype == "politician"
    assert components.slug == "ram-chandra-poudel"


def test_break_entity_id_without_subtype():
    """Test breaking entity ID without subtype."""
    from nes2.core.identifiers.builders import break_entity_id
    
    components = break_entity_id("entity:person/ram-chandra-poudel")
    assert components.type == "person"
    assert components.subtype is None
    assert components.slug == "ram-chandra-poudel"


def test_build_relationship_id():
    """Test building relationship ID."""
    from nes2.core.identifiers.builders import build_relationship_id
    
    rel_id = build_relationship_id(
        "entity:person/politician/ram-chandra-poudel",
        "entity:organization/political_party/nepali-congress",
        "MEMBER_OF"
    )
    assert rel_id == "relationship:person/politician/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF"


def test_break_relationship_id():
    """Test breaking relationship ID."""
    from nes2.core.identifiers.builders import break_relationship_id
    
    components = break_relationship_id(
        "relationship:person/politician/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF"
    )
    assert components.source == "entity:person/politician/ram-chandra-poudel"
    assert components.target == "entity:organization/political_party/nepali-congress"
    assert components.type == "MEMBER_OF"


def test_build_version_id():
    """Test building version ID."""
    from nes2.core.identifiers.builders import build_version_id
    
    version_id = build_version_id("entity:person/politician/ram-chandra-poudel", 1)
    assert version_id == "version:entity:person/politician/ram-chandra-poudel:1"


def test_break_version_id():
    """Test breaking version ID."""
    from nes2.core.identifiers.builders import break_version_id
    
    components = break_version_id("version:entity:person/politician/ram-chandra-poudel:2")
    assert components.entity_or_relationship_id == "entity:person/politician/ram-chandra-poudel"
    assert components.version_number == 2


def test_build_actor_id():
    """Test building actor ID."""
    from nes2.core.identifiers.builders import build_actor_id
    
    actor_id = build_actor_id("csv-importer")
    assert actor_id == "actor:csv-importer"


def test_break_actor_id():
    """Test breaking actor ID."""
    from nes2.core.identifiers.builders import break_actor_id
    
    components = break_actor_id("actor:csv-importer")
    assert components.slug == "csv-importer"
