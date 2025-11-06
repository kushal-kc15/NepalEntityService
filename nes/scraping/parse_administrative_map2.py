"""Parse Nepal administrative map data and create location entities."""

import json
from collections import OrderedDict
from datetime import datetime
from urllib.request import urlopen

from nes.core.identifiers import build_entity_id
from nes.core.models import ADMINISTRATIVE_LEVELS, Location
from nes.core.models.base import Name
from nes.core.models.entity import LocationType
from nes.core.models.version import Actor, Version, VersionSummary
from nes.database import get_database

NEPALI = "https://raw.githubusercontent.com/sagautam5/local-states-nepal/refs/heads/master/dataset/alldataset/np.json"
ENGLISH = "https://raw.githubusercontent.com/sagautam5/local-states-nepal/refs/heads/master/dataset/alldataset/en.json"


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name."""
    return (
        name.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace(".", "")
        .replace(r"\-+", r"\-")
    )


def extract_identifiers_and_attributes(
    data_en: dict, data_ne: dict
) -> tuple[dict, dict]:
    """Extract identifiers and attributes from location data."""
    identifiers = {}
    attributes = {}

    if data_en.get("website", "").strip():
        identifiers["website"] = data_en["website"].strip()
    if data_en.get("area_sq_km", "").strip():
        attributes["sys:area"] = float(data_en["area_sq_km"].strip())
    if data_en.get("headquarter", "").strip():
        attributes["sys:headquarter_en"] = data_en["headquarter"].strip()
    if data_ne.get("headquarter", "").strip():
        attributes["sys:headquarter_ne"] = data_ne["headquarter"].strip()

    return identifiers, attributes


def create_location_entity(
    name_en: str,
    name_ne: str,
    subtype: str,
    parent_id: str = None,
    actor: Actor = None,
    **kwargs,
) -> Location:
    """Create a location entity with both English and Nepali names."""
    slug = create_slug(name_en)
    now = datetime.now()

    names = [
        Name(value=name_en.strip(), lang="en", kind=NameKind.PRIMARY),
        Name(value=name_ne.strip(), lang="ne", kind=NameKind.PRIMARY),
    ]

    entity = Location(
        slug=slug,
        subType=subtype,
        names=names,
        created_at=now,
        version_summary=VersionSummary(
            entity_or_relationship_id=build_entity_id("location", subtype, slug),
            type="ENTITY",
            version_number=1,
            actor=actor,
            change_description="Imported from Nepal administrative map data",
            created_at=now,
        ),
        attributions=["https://github.com/sagautam5/local-states-nepal"],
        **kwargs,
    )

    entity.locationType = subtype
    if parent_id:
        entity.parentLocation = parent_id
    entity.administrativeLevel = ADMINISTRATIVE_LEVELS.get(subtype)

    return entity


async def save_entity(db, entity: Location):
    """Save entity and version to database."""
    await db.put_entity(entity)

    version = Version.model_validate(
        dict(
            **entity.version_summary.model_dump(),
            snapshot=entity.model_dump(),
            changes={},
        ),
        extra="ignore",
    )
    await db.put_version(version)


async def parse_administrative_map():
    """Parse administrative map data and create location entities."""
    # Fetch data from URLs
    with urlopen(NEPALI) as response:
        nepali_data = json.loads(response.read())

    with urlopen(ENGLISH) as response:
        english_data = json.loads(response.read())

    # Assert ID equality between English and Nepali data
    assert len(english_data) == len(nepali_data), "Province count mismatch"

    db = get_database()
    actor = Actor(slug="location-np-importer", name="Location NP Importer")
    await db.put_actor(actor)

    # Create provinces
    for province_en, province_ne in zip(english_data, nepali_data):
        assert (
            province_en["id"] == province_ne["id"]
        ), f"Province ID mismatch: {province_en['id']} != {province_ne['id']}"

        identifiers, attributes = extract_identifiers_and_attributes(
            province_en, province_ne
        )
        province = create_location_entity(
            province_en["name"],
            province_ne["name"],
            "province",
            actor=actor,
            identifiers=identifiers,
            attributes=attributes,
        )
        await save_entity(db, province)
        print(f"Created province: {province_en['name']} ({province_ne['name']})")

        province_id = build_entity_id(
            "location", "province", create_slug(province_en["name"])
        )

        # Create districts
        assert len(province_en["districts"]) == len(
            province_ne["districts"]
        ), f"District count mismatch in province {province_en['name']}"

        for district_en, district_ne in zip(
            province_en["districts"], province_ne["districts"]
        ):
            if isinstance(district_en, (str, int)):
                district_en = province_en["districts"][district_en]
                district_ne = province_ne["districts"][district_ne]
            assert (
                district_en["id"] == district_ne["id"]
            ), f"District ID mismatch: {district_en['id']} != {district_ne['id']}"

            identifiers, attributes = extract_identifiers_and_attributes(
                district_en, district_ne
            )
            district = create_location_entity(
                district_en["name"],
                district_ne["name"],
                "district",
                province_id,
                actor,
                identifiers=identifiers,
                attributes=attributes,
            )
            await save_entity(db, district)
            print(f"Created district: {district_en['name']} ({district_ne['name']})")

            district_id = build_entity_id(
                "location", "district", create_slug(district_en["name"])
            )

            # Create municipalities
            assert len(district_en["municipalities"]) == len(
                district_ne["municipalities"]
            ), f"Municipality count mismatch in district {district_en['name']}"

            for municipality_en, municipality_ne in zip(
                district_en["municipalities"], district_ne["municipalities"]
            ):
                if isinstance(municipality_en, (str, int)):
                    municipality_en = district_en["municipalities"][municipality_en]
                    municipality_ne = district_ne["municipalities"][municipality_ne]
                assert (
                    municipality_en["id"] == municipality_ne["id"]
                ), f"Municipality ID mismatch: {municipality_en['id']} != {municipality_ne['id']}"

                # Determine municipality type based on category_id
                category_map = {
                    1: "metropolitan_city",
                    2: "sub_metropolitan_city",
                    3: "municipality",
                    4: "rural_municipality",
                }
                subtype = category_map.get(
                    municipality_en["category_id"], "municipality"
                )

                identifiers, attributes = extract_identifiers_and_attributes(
                    municipality_en, municipality_ne
                )
                municipality = create_location_entity(
                    municipality_en["name"],
                    municipality_ne["name"],
                    subtype,
                    district_id,
                    actor,
                    identifiers=identifiers,
                    attributes=attributes,
                )
                await save_entity(db, municipality)
                print(
                    f"Created {subtype}: {municipality_en['name']} ({municipality_ne['name']})"
                )

                municipality_id = build_entity_id(
                    "location", subtype, create_slug(municipality_en["name"])
                )

                # Create wards
                assert len(municipality_en["wards"]) == len(
                    municipality_ne["wards"]
                ), f"Ward mismatch in {municipality_en['name']}"

                for ward_num in municipality_en["wards"]:
                    ward_en = f"{municipality_en['name'].strip()} - Ward {ward_num}"
                    ward_ne = f"{municipality_ne['name'].strip()} वडा नं.– {ward_num}"
                    ward = create_location_entity(
                        ward_en, ward_ne, "ward", municipality_id, actor
                    )
                    await save_entity(db, ward)
                    print(f"Created ward: {ward_en} ({ward_ne})")

    for location_type in LocationType:
        entities = await db.list_entities(
            limit=10_000, type="location", subtype=location_type.value
        )
        print(f"{len(entities)} {location_type.value} entities found.")

    print("All done!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(parse_administrative_map())
