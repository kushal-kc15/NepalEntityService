"""Helper functions for nes2 tests."""

from typing import Dict, Any
from datetime import datetime


def create_test_entity(
    slug: str,
    entity_type: str,
    sub_type: str,
    name_en: str,
    name_ne: str = None,
    attributes: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a test entity with minimal required fields."""
    entity = {
        "slug": slug,
        "type": entity_type,
        "sub_type": sub_type,
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": name_en}
            }
        ]
    }
    
    if name_ne:
        entity["names"][0]["ne"] = {"full": name_ne}
    
    if attributes:
        entity["attributes"] = attributes
    
    return entity


def create_test_relationship(
    source_id: str,
    target_id: str,
    relationship_type: str,
    start_date: str = None,
    end_date: str = None,
    attributes: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a test relationship with minimal required fields."""
    relationship = {
        "source_entity_id": source_id,
        "target_entity_id": target_id,
        "type": relationship_type
    }
    
    if start_date:
        relationship["start_date"] = start_date
    
    if end_date:
        relationship["end_date"] = end_date
    
    if attributes:
        relationship["attributes"] = attributes
    
    return relationship


def create_test_version(
    entity_id: str,
    version: int,
    snapshot: Dict[str, Any],
    author_id: str = "author:system:test",
    change_description: str = "Test change"
) -> Dict[str, Any]:
    """Create a test version with minimal required fields."""
    from datetime import UTC
    return {
        "entity_id": entity_id,
        "version": version,
        "snapshot": snapshot,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "created_by": author_id,
        "change_description": change_description
    }


def assert_entity_equal(entity1: Dict[str, Any], entity2: Dict[str, Any], ignore_fields: list = None):
    """Assert that two entities are equal, optionally ignoring certain fields."""
    ignore_fields = ignore_fields or []
    
    for key in entity1:
        if key in ignore_fields:
            continue
        assert key in entity2, f"Key '{key}' missing in entity2"
        assert entity1[key] == entity2[key], f"Value mismatch for key '{key}'"


def assert_relationship_equal(rel1: Dict[str, Any], rel2: Dict[str, Any], ignore_fields: list = None):
    """Assert that two relationships are equal, optionally ignoring certain fields."""
    ignore_fields = ignore_fields or []
    
    for key in rel1:
        if key in ignore_fields:
            continue
        assert key in rel2, f"Key '{key}' missing in rel2"
        assert rel1[key] == rel2[key], f"Value mismatch for key '{key}'"
