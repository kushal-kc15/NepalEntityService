"""Entity type/subtype to class mapping."""

from nes.core.models.entity import EntitySubType, EntityType
from nes.core.models.location import Location, LocationType
from nes.core.models.organization import (GovernmentBody, Organization,
                                          PoliticalParty)
from nes.core.models.person import Person

ENTITY_TYPE_MAP = {
    EntityType.PERSON: {
        None: Person,
    },
    EntityType.ORGANIZATION: {
        None: Organization,
        EntitySubType.POLITICAL_PARTY: PoliticalParty,
        EntitySubType.GOVERNMENT_BODY: GovernmentBody,
    },
    EntityType.LOCATION: {
        None: Location,
        **{
            key: Location
            for key in EntitySubType
            if key.value in [lt.value for lt in LocationType]
        },
    },
}
