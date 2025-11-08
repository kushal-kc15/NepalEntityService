"""ID builder functions for nes2."""

from typing import NamedTuple


class EntityIdComponents(NamedTuple):
    type: str
    subtype: str | None
    slug: str


class RelationshipIdComponents(NamedTuple):
    source: str
    target: str
    type: str


class ActorIdComponents(NamedTuple):
    slug: str


class VersionIdComponents(NamedTuple):
    entity_or_relationship_id: str
    version_number: int


def _build_entity_id_core(type: str, subtype: str | None, slug: str) -> str:
    """Build entity ID in format: entity:<type>/<subtype>/<slug> or entity:<type>/<slug> if subtype is None."""
    if subtype is None:
        return f"{type}/{slug}"
    return f"{type}/{subtype}/{slug}"


def build_entity_id(type: str, subtype: str | None, slug: str) -> str:
    """Build entity ID in format: entity:<type>/<subtype>/<slug> or entity:<type>/<slug> if subtype is None.

    Example:
        >>> build_entity_id("person", "politician", "ram-chandra-poudel")
        "entity:person/politician/ram-chandra-poudel"
        >>> build_entity_id("person", None, "ram-chandra-poudel")
        "entity:person/ram-chandra-poudel"
    """
    return f"entity:{_build_entity_id_core(type, subtype, slug)}"


def break_entity_id(entity_id: str) -> EntityIdComponents:
    """Break entity ID into components: EntityIdComponents(type, subtype, slug).

    Example:
        >>> break_entity_id("entity:person/politician/ram-chandra-poudel")
        EntityIdComponents(type='person', subtype='politician', slug='ram-chandra-poudel')
        >>> break_entity_id("entity:person/ram-chandra-poudel")
        EntityIdComponents(type='person', subtype=None, slug='ram-chandra-poudel')
    """
    if not entity_id.startswith("entity:"):
        raise ValueError("Invalid entity ID format")

    parts = entity_id[7:].split("/")  # Remove "entity:" prefix
    if len(parts) == 2:
        return EntityIdComponents(type=parts[0], subtype=None, slug=parts[1])
    elif len(parts) == 3:
        return EntityIdComponents(type=parts[0], subtype=parts[1], slug=parts[2])
    else:
        raise ValueError("Invalid entity ID format")


def build_relationship_id(source: str, target: str, type: str) -> str:
    """Build relationship ID in format: relationship:<source>:<target>:<type>.

    Example:
        >>> build_relationship_id("entity:person/politician/ram-chandra-poudel", "entity:organization/political_party/nepali-congress", "MEMBER_OF")
        "relationship:person/politician/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF"
    """
    # Extract ID parts without "entity:" prefix
    source_part = (
        source.replace("entity:", "") if source.startswith("entity:") else source
    )
    target_part = (
        target.replace("entity:", "") if target.startswith("entity:") else target
    )
    return f"relationship:{source_part}:{target_part}:{type}"


def break_relationship_id(relationship_id: str) -> RelationshipIdComponents:
    """Break relationship ID into components: RelationshipIdComponents(source, target, type).

    Example:
        >>> break_relationship_id("relationship:person/politician/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF")
        RelationshipIdComponents(source='entity:person/politician/ram-chandra-poudel', target='entity:organization/political_party/nepali-congress', type='MEMBER_OF')
    """
    if not relationship_id.startswith("relationship:"):
        raise ValueError("Invalid relationship ID format")

    # Remove "relationship:" prefix
    remaining = relationship_id[13:]

    # Split by ':' to get source, target, type
    parts = remaining.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid relationship ID format")

    source_part, target_part, rel_type = parts

    # Convert back to proper entity IDs
    source = f"entity:{source_part}"
    target = f"entity:{target_part}"

    return RelationshipIdComponents(source=source, target=target, type=rel_type)


def build_actor_id(slug: str) -> str:
    """Build actor ID in format: actor:<slug>.

    Example:
        >>> build_actor_id("csv-importer")
        "actor:csv-importer"
    """
    return f"actor:{slug}"


def break_actor_id(actor_id: str) -> ActorIdComponents:
    """Break actor ID into components: ActorIdComponents(slug).

    Example:
        >>> break_actor_id("actor:csv-importer")
        ActorIdComponents(slug='csv-importer')
    """
    if not actor_id.startswith("actor:"):
        raise ValueError("Invalid actor ID format")

    slug = actor_id[6:]  # Remove "actor:" prefix
    return ActorIdComponents(slug=slug)


def build_version_id(entity_or_relationship_id: str, version_number: int) -> str:
    """Build version ID in format: version:<entity_or_relationship_id>:<version_number>.

    Example:
        >>> build_version_id("entity:person/politician/ram-chandra-poudel", 1)
        "version:entity:person/politician/ram-chandra-poudel:1"
        >>> build_version_id("relationship:person/politician/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF", 2)
        "version:relationship:person/politician/ram-chandra-poudel:organization/political_party/nepali-congress:MEMBER_OF:2"
    """
    return f"version:{entity_or_relationship_id}:{version_number}"


def break_version_id(version_id: str) -> VersionIdComponents:
    """Break version ID into components: VersionIdComponents(entity_or_relationship_id, version_number).

    Example:
        >>> break_version_id("version:entity:person/politician/ram-chandra-poudel:1")
        VersionIdComponents(entity_or_relationship_id='entity:person/politician/ram-chandra-poudel', version_number=1)
    """
    if not version_id.startswith("version:"):
        raise ValueError("Invalid version ID format")

    # Remove "version:" prefix
    remaining = version_id[8:]

    # Check if it's an entity or relationship ID
    if remaining.startswith("entity:"):
        # For entity IDs: version:entity:type/subtype/slug:version_number
        # Split after "entity:" to separate the entity part from version
        entity_part = remaining[7:]  # Remove "entity:" prefix
        parts = entity_part.rsplit(":", 1)
        if len(parts) != 2:
            raise ValueError("Invalid version ID format")
        entity_core, version_str = parts
        entity_id = f"entity:{entity_core}"
    elif remaining.startswith("relationship:"):
        # For relationship IDs: version:relationship:source:target:type:version_number
        # Need to find the last colon that separates the version number
        parts = remaining.rsplit(":", 1)
        if len(parts) != 2:
            raise ValueError("Invalid version ID format")
        relationship_id, version_str = parts
        entity_id = relationship_id
    else:
        raise ValueError("Version ID must contain entity or relationship ID")

    try:
        version_number = int(version_str)
    except ValueError:
        raise ValueError("Invalid version number format")

    return VersionIdComponents(
        entity_or_relationship_id=entity_id, version_number=version_number
    )
