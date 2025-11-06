"""Test cases for identifier builders and breakers."""

import pytest

from nes.core.identifiers import (ActorIdComponents, EntityIdComponents,
                                  RelationshipIdComponents,
                                  VersionIdComponents, break_actor_id,
                                  break_entity_id, break_relationship_id,
                                  break_version_id, build_actor_id,
                                  build_entity_id, build_relationship_id,
                                  build_version_id)


class TestEntityId:
    def test_build_entity_id(self):
        result = build_entity_id("person", None, "harka-sampang")
        assert result == "entity:person/harka-sampang"

    def test_build_entity_id_organization(self):
        result = build_entity_id("organization", "party", "shram-sanskriti-party")
        assert result == "entity:organization/party/shram-sanskriti-party"

    def test_break_entity_id(self):
        result = break_entity_id("entity:person/harka-sampang")
        assert result == EntityIdComponents(
            type="person", subtype=None, slug="harka-sampang"
        )

    def test_break_entity_id_organization(self):
        result = break_entity_id("entity:organization/party/shram-sanskriti-party")
        assert result == EntityIdComponents(
            type="organization", subtype="party", slug="shram-sanskriti-party"
        )

    def test_break_entity_id_invalid_prefix(self):
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            break_entity_id("invalid:person/harka-sampang")

    def test_break_entity_id_single_part(self):
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            break_entity_id("entity:person")

    def test_break_entity_id_too_many_parts(self):
        with pytest.raises(ValueError, match="Invalid entity ID format"):
            break_entity_id("entity:person/harka/sampang/lampang")

    def test_build_entity_id_no_subtype(self):
        result = build_entity_id("person", None, "harka-sampang")
        assert result == "entity:person/harka-sampang"

    def test_build_entity_id_organization_no_subtype(self):
        result = build_entity_id("organization", None, "red-cross-nepal")
        assert result == "entity:organization/red-cross-nepal"

    def test_break_entity_id_no_subtype(self):
        result = break_entity_id("entity:person/harka-sampang")
        assert result == EntityIdComponents(
            type="person", subtype=None, slug="harka-sampang"
        )

    def test_break_entity_id_organization_no_subtype(self):
        result = break_entity_id("entity:organization/red-cross-nepal")
        assert result == EntityIdComponents(
            type="organization", subtype=None, slug="red-cross-nepal"
        )

    def test_roundtrip_entity_id(self):
        original = "entity:person/harka-sampang"
        components = break_entity_id(original)
        rebuilt = build_entity_id(components.type, components.subtype, components.slug)
        assert rebuilt == original

    def test_roundtrip_entity_id_no_subtype(self):
        original = "entity:person/harka-sampang"
        components = break_entity_id(original)
        rebuilt = build_entity_id(components.type, components.subtype, components.slug)
        assert rebuilt == original


class TestRelationshipId:
    def test_build_relationship_id_with_entity_prefix(self):
        result = build_relationship_id(
            "entity:person/harka-sampang",
            "entity:organization/party/shram-sanskriti-party",
            "MEMBER_OF",
        )
        assert (
            result
            == "relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF"
        )

    def test_build_relationship_id_without_entity_prefix(self):
        result = build_relationship_id(
            "person/harka-sampang",
            "organization/party/shram-sanskriti-party",
            "MEMBER_OF",
        )
        assert (
            result
            == "relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF"
        )

    def test_break_relationship_id(self):
        result = break_relationship_id(
            "relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF"
        )
        assert result == RelationshipIdComponents(
            source="entity:person/harka-sampang",
            target="entity:organization/party/shram-sanskriti-party",
            type="MEMBER_OF",
        )

    def test_break_relationship_id_invalid_prefix(self):
        with pytest.raises(ValueError, match="Invalid relationship ID format"):
            break_relationship_id(
                "invalid:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF"
            )

    def test_break_relationship_id_missing_parts(self):
        with pytest.raises(ValueError, match="Invalid relationship ID format"):
            break_relationship_id("relationship:person/harka-sampang:organization")

    def test_break_relationship_id_too_many_parts(self):
        with pytest.raises(ValueError, match="Invalid relationship ID format"):
            break_relationship_id(
                "relationship:person:politician:harka:sampang:organization:party"
            )

    def test_roundtrip_relationship_id(self):
        source = "entity:person/harka-sampang"
        target = "entity:organization/party/shram-sanskriti-party"
        rel_type = "MEMBER_OF"

        built = build_relationship_id(source, target, rel_type)
        components = break_relationship_id(built)

        assert components.source == source
        assert components.target == target
        assert components.type == rel_type


class TestActorId:
    def test_build_actor_id(self):
        result = build_actor_id("system-admin")
        assert result == "actor:system-admin"

    def test_build_actor_id_with_dashes(self):
        result = build_actor_id("data-migration-bot")
        assert result == "actor:data-migration-bot"

    def test_break_actor_id(self):
        result = break_actor_id("actor:system-admin")
        assert result == ActorIdComponents(slug="system-admin")

    def test_break_actor_id_with_dashes(self):
        result = break_actor_id("actor:data-migration-bot")
        assert result == ActorIdComponents(slug="data-migration-bot")

    def test_break_actor_id_invalid_prefix(self):
        with pytest.raises(ValueError, match="Invalid actor ID format"):
            break_actor_id("invalid:system-admin")

    def test_roundtrip_actor_id(self):
        original = "actor:system-admin"
        components = break_actor_id(original)
        rebuilt = build_actor_id(components.slug)
        assert rebuilt == original


class TestVersionId:
    def test_build_version_id_entity(self):
        result = build_version_id("entity:person/harka-sampang", 1)
        assert result == "version:entity:person/harka-sampang:1"

    def test_build_version_id_relationship(self):
        result = build_version_id(
            "relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF",
            2,
        )
        assert (
            result
            == "version:relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF:2"
        )

    def test_break_version_id_entity(self):
        result = break_version_id("version:entity:person/harka-sampang:1")
        assert result == VersionIdComponents(
            entity_or_relationship_id="entity:person/harka-sampang",
            version_number=1,
        )

    def test_break_version_id_relationship(self):
        result = break_version_id(
            "version:relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF:2"
        )
        assert result == VersionIdComponents(
            entity_or_relationship_id="relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF",
            version_number=2,
        )

    def test_break_version_id_invalid_prefix(self):
        with pytest.raises(ValueError, match="Invalid version ID format"):
            break_version_id("invalid:entity:person/harka-sampang:1")

    def test_break_version_id_invalid_entity_type(self):
        with pytest.raises(
            ValueError, match="Version ID must contain entity or relationship ID"
        ):
            break_version_id("version:invalid:person/harka-sampang:1")

    def test_break_version_id_invalid_version_number(self):
        with pytest.raises(ValueError, match="Invalid version number format"):
            break_version_id("version:entity:person/harka-sampang:invalid")

    def test_break_version_id_missing_version_number(self):
        with pytest.raises(ValueError, match="Invalid version ID format"):
            break_version_id("version:entity:person/harka-sampang")

    def test_roundtrip_version_id_entity(self):
        entity_id = "entity:person/harka-sampang"
        version_num = 5

        built = build_version_id(entity_id, version_num)
        components = break_version_id(built)

        assert components.entity_or_relationship_id == entity_id
        assert components.version_number == version_num

    def test_build_version_id_entity_no_subtype(self):
        result = build_version_id("entity:person/harka-sampang", 1)
        assert result == "version:entity:person/harka-sampang:1"

    def test_break_version_id_entity_no_subtype(self):
        result = break_version_id("version:entity:person/harka-sampang:1")
        assert result == VersionIdComponents(
            entity_or_relationship_id="entity:person/harka-sampang", version_number=1
        )

    def test_roundtrip_version_id_entity_no_subtype(self):
        entity_id = "entity:person/harka-sampang"
        version_num = 2

        built = build_version_id(entity_id, version_num)
        components = break_version_id(built)

        assert components.entity_or_relationship_id == entity_id
        assert components.version_number == version_num

    def test_roundtrip_version_id_relationship(self):
        relationship_id = "relationship:person/harka-sampang:organization/party/shram-sanskriti-party:MEMBER_OF"
        version_num = 3

        built = build_version_id(relationship_id, version_num)
        components = break_version_id(built)

        assert components.entity_or_relationship_id == relationship_id
        assert components.version_number == version_num


class TestEdgeCases:
    def test_entity_id_with_special_characters(self):
        # Test with underscores and numbers
        result = build_entity_id("gov_body", "ministry_office", "finance-ministry-2024")
        assert result == "entity:gov_body/ministry_office/finance-ministry-2024"

        components = break_entity_id(result)
        assert components.type == "gov_body"
        assert components.subtype == "ministry_office"
        assert components.slug == "finance-ministry-2024"

    def test_relationship_with_no_subtype_entities(self):
        source = "entity:person/ram-bahadur-thapa"
        target = "entity:organization/red-cross-nepal"

        result = build_relationship_id(source, target, "VOLUNTEER_AT")
        components = break_relationship_id(result)

        assert components.source == source
        assert components.target == target
        assert components.type == "VOLUNTEER_AT"

    def test_relationship_with_complex_ids(self):
        source = "entity:person/civil_servant/ram-bahadur-thapa"
        target = "entity:gov_body/ministry/home-affairs-ministry"

        result = build_relationship_id(source, target, "EMPLOYED_BY")
        components = break_relationship_id(result)

        assert components.source == source
        assert components.target == target
        assert components.type == "EMPLOYED_BY"

    def test_version_id_high_numbers(self):
        entity_id = "entity:organization/ngo/red-cross-nepal"
        version_num = 999

        built = build_version_id(entity_id, version_num)
        components = break_version_id(built)

        assert components.entity_or_relationship_id == entity_id
        assert components.version_number == version_num

    def test_version_id_no_subtype_high_numbers(self):
        entity_id = "entity:organization/red-cross-nepal"
        version_num = 1000

        built = build_version_id(entity_id, version_num)
        components = break_version_id(built)

        assert components.entity_or_relationship_id == entity_id
        assert components.version_number == version_num

    def test_actor_id_empty_slug(self):
        # This should work as the slug validation is handled elsewhere
        result = build_actor_id("")
        assert result == "actor:"

        components = break_actor_id(result)
        assert components.slug == ""
