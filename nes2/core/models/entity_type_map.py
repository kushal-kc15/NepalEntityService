"""Entity type/subtype mapping for nes2."""

from nes2.core.models.entity import EntitySubType, EntityType

# Simplified entity type map for v2
# This maps entity types to their allowed subtypes
ENTITY_TYPE_MAP = {
    EntityType.PERSON: {
        None,  # Person without subtype
        EntitySubType.POLITICIAN,
    },
    EntityType.ORGANIZATION: {
        None,  # Organization without subtype
        EntitySubType.POLITICAL_PARTY,
        EntitySubType.GOVERNMENT_BODY,
    },
    EntityType.LOCATION: {
        None,  # Location without subtype
        EntitySubType.PROVINCE,
        EntitySubType.DISTRICT,
        EntitySubType.METROPOLITAN_CITY,
        EntitySubType.SUB_METROPOLITAN_CITY,
        EntitySubType.MUNICIPALITY,
        EntitySubType.RURAL_MUNICIPALITY,
        EntitySubType.WARD,
        EntitySubType.CONSTITUENCY,
    },
}
