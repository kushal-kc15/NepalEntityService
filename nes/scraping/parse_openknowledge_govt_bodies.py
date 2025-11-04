"""
Script to parse CSV data and create government bodies.
Source government bodies from https://raw.githubusercontent.com/openknowledgenp/publicbodies-data/refs/heads/master/publicbodies%20data.csv
"""

ATTRIBUTION = "OpenKnowledge Nepal"

import asyncio
import csv
import re
from datetime import datetime
from urllib.request import urlopen

from nes.core.models.base import ContactInfo, Name
from nes.core.models.entity import GovernmentBody, GovernmentType
from nes.core.models.version import Actor, Version, VersionSummary
from nes.database.file_database import FileDatabase


def clean_value(value: str) -> str:
    """Clean CSV value, treating '-' as empty."""
    if not value or value.strip() == "-":
        return ""
    return value.strip()


def create_slug(name: str) -> str:
    """Create a URL-friendly slug from organization name."""
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")


def determine_government_type(name: str, district: str) -> GovernmentType:
    """Determine government type based on organization name."""
    name_lower = name.lower()
    if any(term in name_lower for term in ["ministry", "national"]):
        return GovernmentType.FEDERAL
    elif any(
        term in name_lower for term in ["province", "provincial", "pradesh", "state"]
    ):
        return GovernmentType.PROVINCIAL
    elif any(
        term in name_lower
        for term in [
            "municipality",
            "city",
            "vdc",
            "village development committee",
            "metropolitan",
            "gaunpalika",
            "gaupalika",
            "nagarpalika",
            "municiapality",
            "mahanagarpalika",
        ]
    ):
        return GovernmentType.LOCAL
    else:
        return GovernmentType.UNKNOWN


async def parse_and_create_entities():
    """Parse CSV and create government body entities."""
    db = FileDatabase("entity-db")

    # Create system actor
    actor = Actor(slug="csv-importer", name="CSV Data Importer")
    await db.put_actor(actor)

    csv_url = "https://raw.githubusercontent.com/openknowledgenp/publicbodies-data/refs/heads/master/publicbodies%20data.csv"

    with urlopen(csv_url) as response:
        csv_data = response.read().decode("utf-8")

    reader = csv.DictReader(csv_data.splitlines())
    created_count = 0

    now = datetime.now()

    for row in reader:
        name = clean_value(row["PublicBodies Name"].strip())
        if not name:
            continue

        slug = create_slug(name)
        district = clean_value(row["District"].strip())
        website = clean_value(row["Website URL"].strip())
        address = clean_value(row["PublicBodies Address"].strip())
        email = clean_value(row["PublicBodies Contact Email"].strip())
        phone = clean_value(row["PublicBodies Contact Phone"].strip())

        # Create contacts list
        contacts = []
        if email:
            contacts.append(ContactInfo(type="email", value=email))
        if phone:
            contacts.append(ContactInfo(type="phone", value=phone))
        if website:
            contacts.append(ContactInfo(type="website", value=website))

        # Create government body entity
        entity = GovernmentBody(
            slug=slug,
            names=[Name(kind="DEFAULT", value=name, lang="en")],
            createdAt=now,
            short_description=f"Government body in {district}",
            contacts=contacts if contacts else None,
            attributes={
                "address": address,
                "sys:location:district": district,
                "sys:governmentType": determine_government_type(name, district),
            },
            attributions=[ATTRIBUTION],
            versionSummary=VersionSummary(
                entityOrRelationshipId=f"entity:organization/government-body/{slug}",
                type="ENTITY",
                versionNumber=1,
                actor=actor,
                changeDescription="Initial creation from CSV data",
                createdAt=now,
            ),
        )

        await db.put_entity(entity)

        # Create and publish version
        version = Version.model_validate(
            dict(
                **entity.versionSummary.model_dump(),
                snapshot=entity.model_dump(),
                changes={},
            ),
            extra="ignore",
        )
        await db.put_version(version)

        created_count += 1
        print(f"Created: {name} ({slug})")

    entities: list[GovernmentBody] = await db.list_entities(
        type="organization", subtype="government", limit=500
    )
    print(f"\nTotal entities created: {created_count}")


if __name__ == "__main__":
    asyncio.run(parse_and_create_entities())
