"""
Convenience module for accessing nes2 models.

This module re-exports all models from nes2.core.models for easier imports.
Instead of:
    from nes2.core.models.entity import Entity, EntityType
    from nes2.core.models.base import Name, NameKind, NameParts

You can use:
    from nes2.models import Entity, EntityType, Name, NameKind, NameParts
"""

from nes2.core.models import (
    # Base models
    Address,
    Attribution,
    Contact,
    ContactType,
    EntityPicture,
    EntityPictureType,
    LangText,
    LangTextValue,
    Name,
    NameKind,
    NameParts,
    ProvenanceMethod,
    # Entity models
    Entity,
    EntitySubType,
    EntityType,
    ExternalIdentifier,
    IdentifierScheme,
    # Person models
    Person,
    PersonDetails,
    Gender,
    Education,
    Position,
    ElectoralDetails,
    Candidacy,
    Symbol,
    # Organization models
    Organization,
    PoliticalParty,
    GovernmentBody,
    GovernmentType,
    # Location models
    Location,
    LocationType,
    ADMINISTRATIVE_LEVELS,
    # Relationship models
    Relationship,
    RelationshipType,
    # Version models
    Author,
    Version,
    VersionSummary,
    VersionType,
)

__all__ = [
    # Base models
    "Address",
    "Attribution",
    "Contact",
    "ContactType",
    "EntityPicture",
    "EntityPictureType",
    "LangText",
    "LangTextValue",
    "Name",
    "NameKind",
    "NameParts",
    "ProvenanceMethod",
    # Entity models
    "Entity",
    "EntitySubType",
    "EntityType",
    "ExternalIdentifier",
    "IdentifierScheme",
    # Person models
    "Person",
    "PersonDetails",
    "Gender",
    "Education",
    "Position",
    "ElectoralDetails",
    "Candidacy",
    "Symbol",
    # Organization models
    "Organization",
    "PoliticalParty",
    "GovernmentBody",
    "GovernmentType",
    # Location models
    "Location",
    "LocationType",
    "ADMINISTRATIVE_LEVELS",
    # Relationship models
    "Relationship",
    "RelationshipType",
    # Version models
    "Author",
    "Version",
    "VersionSummary",
    "VersionType",
]
