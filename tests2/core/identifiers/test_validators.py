"""Tests for identifier validators in nes2."""

import pytest


def test_validate_entity_id_valid():
    """Test validating valid entity IDs."""
    from nes2.core.identifiers.validators import validate_entity_id, is_valid_entity_id
    
    # Valid with subtype
    entity_id = "entity:person/ram-chandra-poudel"
    assert is_valid_entity_id(entity_id)
    assert validate_entity_id(entity_id) == entity_id
    
    # Valid without subtype
    entity_id = "entity:person/ram-chandra-poudel"
    assert is_valid_entity_id(entity_id)
    assert validate_entity_id(entity_id) == entity_id


def test_validate_entity_id_invalid_format():
    """Test validating invalid entity ID formats."""
    from nes2.core.identifiers.validators import is_valid_entity_id
    
    # Missing entity: prefix
    assert not is_valid_entity_id("person/ram-chandra-poudel")
    
    # Invalid slug (uppercase)
    assert not is_valid_entity_id("entity:person/Ram-Chandra-Poudel")
    
    # Slug too short
    assert not is_valid_entity_id("entity:person/ab")


def test_validate_relationship_id_valid():
    """Test validating valid relationship IDs."""
    from nes2.core.identifiers.validators import validate_relationship_id, is_valid_relationship_id
    
    rel_id = "relationship:person/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF"
    assert is_valid_relationship_id(rel_id)
    assert validate_relationship_id(rel_id) == rel_id


def test_validate_version_id_valid():
    """Test validating valid version IDs."""
    from nes2.core.identifiers.validators import validate_version_id, is_valid_version_id
    
    version_id = "version:entity:person/ram-chandra-poudel:1"
    assert is_valid_version_id(version_id)
    assert validate_version_id(version_id) == version_id


def test_validate_author_id_valid():
    """Test validating valid author IDs."""
    from nes2.core.identifiers.validators import validate_author_id, is_valid_author_id
    
    author_id = "author:csv-importer"
    assert is_valid_author_id(author_id)
    assert validate_author_id(author_id) == author_id
    
    # Invalid slug (too short)
    assert not is_valid_author_id("author:ab")
