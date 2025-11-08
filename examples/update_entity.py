"""Example: Update an existing entity with automatic versioning.

This example demonstrates how to:
1. Initialize the Publication Service
2. Retrieve an existing entity
3. Modify entity attributes
4. Update the entity with automatic version creation
5. View the version history

The example uses authentic Nepali politician data.
"""

import asyncio
from pathlib import Path

from nes2.database.file_database import FileDatabase
from nes2.services.publication import PublicationService


async def main():
    """Update an entity and track version history."""
    
    # Initialize database and publication service
    db_path = Path("nes-db/v2")
    db = FileDatabase(base_path=str(db_path))
    pub_service = PublicationService(database=db)
    
    print("=" * 70)
    print("Entity Update Example - Ram Chandra Poudel")
    print("=" * 70)
    
    # Entity ID for Ram Chandra Poudel
    entity_id = "entity:person/ram-chandra-poudel"
    
    # Step 1: Retrieve the existing entity
    print(f"\n1. Retrieving entity: {entity_id}")
    entity = await pub_service.get_entity(entity_id)
    
    if not entity:
        print(f"   ❌ Entity not found: {entity_id}")
        print("   Please ensure the entity exists in the database first.")
        return
    
    print(f"   ✓ Found entity: {entity.names[0].en.full}")
    print(f"   Current version: {entity.version_summary.version_number}")
    print(f"   Last updated: {entity.version_summary.created_at}")
    
    # Step 2: Display current attributes
    print(f"\n2. Current attributes:")
    if entity.attributes:
        for key, value in entity.attributes.items():
            print(f"   - {key}: {value}")
    else:
        print("   (No attributes)")
    
    # Step 3: Modify the entity
    print(f"\n3. Updating entity attributes...")
    
    # Add or update attributes
    if not entity.attributes:
        entity.attributes = {}
    
    entity.attributes["position"] = "President of Nepal"
    entity.attributes["term_start"] = "2023-03-13"
    entity.attributes["party"] = "nepali-congress"
    entity.attributes["constituency"] = "Tanahun-1"
    
    # Update the entity with automatic versioning
    updated_entity = await pub_service.update_entity(
        entity=entity,
        author_id="author:human:data-maintainer",
        change_description="Updated position to President of Nepal and added term details"
    )
    
    print(f"   ✓ Entity updated successfully")
    print(f"   New version: {updated_entity.version_summary.version_number}")
    print(f"   Updated by: {updated_entity.version_summary.author.slug}")
    
    # Step 4: Display updated attributes
    print(f"\n4. Updated attributes:")
    for key, value in updated_entity.attributes.items():
        print(f"   - {key}: {value}")
    
    # Step 5: Retrieve version history
    print(f"\n5. Version history:")
    versions = await pub_service.get_entity_versions(entity_id)
    
    for version in versions:
        print(f"\n   Version {version.version_number}:")
        print(f"   - Created: {version.created_at}")
        print(f"   - Author: {version.author.slug}")
        print(f"   - Description: {version.change_description or '(no description)'}")
        
        # Show what changed in this version
        if version.snapshot and "attributes" in version.snapshot:
            attrs = version.snapshot.get("attributes", {})
            if attrs:
                print(f"   - Attributes: {', '.join(attrs.keys())}")
    
    print("\n" + "=" * 70)
    print("✓ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
