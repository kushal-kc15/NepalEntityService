"""Test cases for identifier validators."""

import pytest

from nes.core.identifiers import (is_valid_actor_id, is_valid_entity_id,
                                  is_valid_relationship_id,
                                  is_valid_version_id, validate_actor_id,
                                  validate_entity_id, validate_relationship_id,
                                  validate_version_id)


class TestEntityIdValidators:
    def test_valid_entity_id(self):
        entity_id = "entity:person/harka-sampang"
        assert is_valid_entity_id(entity_id) is True
        assert validate_entity_id(entity_id) == entity_id

    def test_valid_entity_id_organization(self):
        entity_id = "entity:organization/political_party/rastriya-swatantra-party"
        assert is_valid_entity_id(entity_id) is True
        assert validate_entity_id(entity_id) == entity_id

    def test_valid_entity_id_min_length_slug(self):
        entity_id = "entity:person/abc"
        assert is_valid_entity_id(entity_id) is True
        assert validate_entity_id(entity_id) == entity_id

    def test_valid_entity_id_max_length_slug(self):
        long_slug = "a" * 64
        entity_id = f"entity:person/{long_slug}"
        assert is_valid_entity_id(entity_id) is True
        assert validate_entity_id(entity_id) == entity_id

    def test_invalid_entity_id_wrong_prefix(self):
        entity_id = "invalid:person/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            validate_entity_id(entity_id)

    def test_invalid_entity_id_no_prefix(self):
        entity_id = "person/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            validate_entity_id(entity_id)

    def test_invalid_entity_id_single_part(self):
        entity_id = "entity:person"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            validate_entity_id(entity_id)

    def test_invalid_entity_id_too_many_parts(self):
        entity_id = "entity:person/harka/sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError):
            validate_entity_id(entity_id)

    def test_invalid_entity_type_uppercase(self):
        entity_id = "entity:Person/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError):
            validate_entity_id(entity_id)

    def test_invalid_entity_type_special_chars(self):
        entity_id = "entity:per-son$/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError):
            validate_entity_id(entity_id)

    def test_invalid_entity_type_too_long(self):
        long_type = "a" * 17
        entity_id = f"entity:{long_type}/politician/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Entity type too long"):
            validate_entity_id(entity_id)

    def test_invalid_entity_subtype_special_chars(self):
        entity_id = "entity:person/poli-tician/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError):
            validate_entity_id(entity_id)

    def test_invalid_entity_subtype_too_long(self):
        long_subtype = "a" * 27
        entity_id = f"entity:person/{long_subtype}/harka-sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError):
            validate_entity_id(entity_id)

    def test_invalid_entity_slug_too_short(self):
        entity_id = "entity:person/ab"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Entity slug length invalid"):
            validate_entity_id(entity_id)

    def test_invalid_entity_slug_too_long(self):
        long_slug = "a" * 101
        entity_id = f"entity:person/{long_slug}"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Entity slug length invalid"):
            validate_entity_id(entity_id)

    def test_invalid_entity_slug_uppercase(self):
        entity_id = "entity:person/Harka-Sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Invalid entity slug format"):
            validate_entity_id(entity_id)

    def test_invalid_entity_slug_special_chars(self):
        entity_id = "entity:person/harka_sampang"
        assert is_valid_entity_id(entity_id) is False
        with pytest.raises(ValueError, match="Invalid entity slug format"):
            validate_entity_id(entity_id)

    def test_empty_entity_id(self):
        assert is_valid_entity_id("") is False
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            validate_entity_id("")

    def test_none_entity_id(self):
        with pytest.raises(AttributeError):
            is_valid_entity_id(None)


class TestRelationshipIdValidators:
    def test_valid_relationship_id(self):
        rel_id = "relationship:person/harka-sampang:organization/political_party/rastriya-swatantra-party:MEMBER_OF"
        assert is_valid_relationship_id(rel_id) is True
        assert validate_relationship_id(rel_id) == rel_id

    def test_valid_relationship_id_no_subtype(self):
        rel_id = "relationship:person/harka-sampang:organization/red-cross-nepal:VOLUNTEER_AT"
        assert is_valid_relationship_id(rel_id) is True
        assert validate_relationship_id(rel_id) == rel_id

    def test_invalid_relationship_id_wrong_prefix(self):
        rel_id = "invalid:person/harka-sampang:organization/party/rastriya-swatantra-party:MEMBER_OF"
        assert is_valid_relationship_id(rel_id) is False
        with pytest.raises(ValueError, match="Invalid relationship ID format"):
            validate_relationship_id(rel_id)

    def test_invalid_relationship_id_missing_parts(self):
        rel_id = "relationship:person/harka-sampang:organization"
        assert is_valid_relationship_id(rel_id) is False
        with pytest.raises(ValueError, match="Invalid relationship ID format"):
            validate_relationship_id(rel_id)

    def test_invalid_relationship_id_bad_source_entity(self):
        rel_id = "relationship:INVALID/politician/harka-sampang:organization/party/rastriya-swatantra-party:MEMBER_OF"
        assert is_valid_relationship_id(rel_id) is False
        with pytest.raises(ValueError):
            validate_relationship_id(rel_id)

    def test_invalid_relationship_id_bad_target_entity(self):
        rel_id = "relationship:person/harka-sampang:INVALID/party/rastriya-swatantra-party:MEMBER_OF"
        assert is_valid_relationship_id(rel_id) is False
        with pytest.raises(ValueError):
            validate_relationship_id(rel_id)

    def test_empty_relationship_id(self):
        assert is_valid_relationship_id("") is False
        with pytest.raises(ValueError, match="Invalid relationship ID format"):
            validate_relationship_id("")


class TestVersionIdValidators:
    def test_valid_version_id_entity(self):
        version_id = "version:entity:person/harka-sampang:1"
        assert is_valid_version_id(version_id) is True
        assert validate_version_id(version_id) == version_id

    def test_valid_version_id_entity_organization(self):
        version_id = "version:entity:organization/political_party/rastriya-party:5"
        assert is_valid_version_id(version_id) is True
        assert validate_version_id(version_id) == version_id

    def test_valid_version_id_relationship(self):
        version_id = "version:relationship:person/harka-sampang:organization/political_party/rastriya-swatantra-party:MEMBER_OF:2"
        assert is_valid_version_id(version_id) is True
        assert validate_version_id(version_id) == version_id

    def test_valid_version_id_high_number(self):
        version_id = "version:entity:person/harka-sampang:999"
        assert is_valid_version_id(version_id) is True
        assert validate_version_id(version_id) == version_id

    def test_invalid_version_id_wrong_prefix(self):
        version_id = "invalid:entity:person/harka-sampang:1"
        assert is_valid_version_id(version_id) is False
        with pytest.raises(ValueError, match="Invalid version ID format"):
            validate_version_id(version_id)

    def test_invalid_version_id_bad_entity(self):
        version_id = "version:entity:INVALID/politician/harka-sampang:1"
        assert is_valid_version_id(version_id) is False
        with pytest.raises(ValueError):
            validate_version_id(version_id)

    def test_invalid_version_id_bad_relationship(self):
        version_id = "version:relationship:INVALID/politician/harka-sampang:organization/party/rastriya-swatantra-party:MEMBER_OF:1"
        assert is_valid_version_id(version_id) is False
        with pytest.raises(ValueError):
            validate_version_id(version_id)

    def test_invalid_version_id_missing_version_number(self):
        version_id = "version:entity:person/harka-sampang"
        assert is_valid_version_id(version_id) is False
        with pytest.raises(ValueError, match="Invalid version ID format"):
            validate_version_id(version_id)

    def test_invalid_version_id_bad_version_number(self):
        version_id = "version:entity:person/harka-sampang:abc"
        assert is_valid_version_id(version_id) is False
        with pytest.raises(ValueError, match="Invalid version number format"):
            validate_version_id(version_id)

    def test_invalid_version_id_unknown_type(self):
        version_id = "version:unknown:person/harka-sampang:1"
        assert is_valid_version_id(version_id) is False
        with pytest.raises(
            ValueError, match="Version ID must contain entity or relationship ID"
        ):
            validate_version_id(version_id)

    def test_empty_version_id(self):
        assert is_valid_version_id("") is False
        with pytest.raises(ValueError, match="Invalid version ID format"):
            validate_version_id("")


class TestActorIdValidators:
    def test_valid_actor_id(self):
        actor_id = "actor:system-admin"
        assert is_valid_actor_id(actor_id) is True
        assert validate_actor_id(actor_id) == actor_id

    def test_valid_actor_id_with_numbers(self):
        actor_id = "actor:user-123"
        assert is_valid_actor_id(actor_id) is True
        assert validate_actor_id(actor_id) == actor_id

    def test_valid_actor_id_min_length(self):
        actor_id = "actor:abc"
        assert is_valid_actor_id(actor_id) is True
        assert validate_actor_id(actor_id) == actor_id

    def test_valid_actor_id_max_length(self):
        long_slug = "a" * 64
        actor_id = f"actor:{long_slug}"
        assert is_valid_actor_id(actor_id) is True
        assert validate_actor_id(actor_id) == actor_id

    def test_invalid_actor_id_wrong_prefix(self):
        actor_id = "invalid:system-admin"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Invalid actor ID format"):
            validate_actor_id(actor_id)

    def test_invalid_actor_id_no_prefix(self):
        actor_id = "system-admin"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Invalid actor ID format"):
            validate_actor_id(actor_id)

    def test_invalid_actor_id_slug_too_short(self):
        actor_id = "actor:ab"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Actor slug length invalid"):
            validate_actor_id(actor_id)

    def test_invalid_actor_id_slug_too_long(self):
        long_slug = "a" * 101
        actor_id = f"actor:{long_slug}"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Actor slug length invalid"):
            validate_actor_id(actor_id)

    def test_invalid_actor_id_uppercase(self):
        actor_id = "actor:System-Admin"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Invalid actor slug format"):
            validate_actor_id(actor_id)

    def test_invalid_actor_id_special_chars(self):
        actor_id = "actor:system_admin"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Invalid actor slug format"):
            validate_actor_id(actor_id)

    def test_invalid_actor_id_spaces(self):
        actor_id = "actor:system admin"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Invalid actor slug format"):
            validate_actor_id(actor_id)

    def test_empty_actor_id(self):
        assert is_valid_actor_id("") is False
        with pytest.raises(ValueError, match="Invalid actor ID format"):
            validate_actor_id("")

    def test_actor_id_empty_slug(self):
        actor_id = "actor:"
        assert is_valid_actor_id(actor_id) is False
        with pytest.raises(ValueError, match="Actor slug length invalid"):
            validate_actor_id(actor_id)


class TestEdgeCases:
    def test_whitespace_handling(self):
        # Leading/trailing whitespace should fail
        assert is_valid_entity_id(" entity:person/harka-sampang ") is False
        assert (
            is_valid_relationship_id(
                " relationship:person/harka:organization/party:MEMBER_OF "
            )
            is False
        )
        assert is_valid_version_id(" version:entity:person/harka:1 ") is False
        assert is_valid_actor_id(" actor:admin ") is False

    def test_unicode_characters(self):
        # Unicode characters should fail validation
        assert is_valid_entity_id("entity:person/हर्क-साम्पाङ") is False
        assert is_valid_actor_id("actor:प्रशासक") is False

    def test_boundary_values(self):
        # Test exact boundary values
        min_slug = "a" * 3
        max_slug = "a" * 64
        max_type = "a" * 16

        assert is_valid_entity_id(f"entity:person/{max_slug}") is True
        assert is_valid_actor_id(f"actor:{max_slug}") is True

    def test_case_sensitivity(self):
        # All validators should be case-sensitive
        assert is_valid_entity_id("ENTITY:person/harka-sampang") is False
        assert (
            is_valid_relationship_id(
                "RELATIONSHIP:person/harka:organization/party:MEMBER_OF"
            )
            is False
        )
        assert is_valid_version_id("VERSION:entity:person/harka:1") is False
        assert is_valid_actor_id("ACTOR:admin") is False

    def test_malformed_colons_and_slashes(self):
        # Test various malformed separators
        assert is_valid_entity_id("entity::person/harka-sampang") is False
        assert is_valid_entity_id("entity:person//harka-sampang") is False
        assert (
            is_valid_relationship_id(
                "relationship::person/harka::organization/party::MEMBER_OF"
            )
            is False
        )
        assert is_valid_version_id("version::entity:person/harka::1") is False
