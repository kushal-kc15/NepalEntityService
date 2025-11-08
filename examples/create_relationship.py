"""Example: Create relationships between entities with automatic versioning.

This example demonstrates how to:
1. Initialize the Publication Service
2. Create relationships between entities (person to organization)
3. Add temporal information (start/end dates)
4. Query relationships for an entity
5. View relationship version history

The example uses authentic Nepali political data.
"""

import asyncio
from datetime import date
from pathlib import Path

from nes2.database.file_database import FileDatabase
from nes2.services.publication import PublicationService
from nes2.services.search import SearchService


async def main():
    """Create relationships between Nepali politicians and political parties."""
    
    # Initialize database and services
    db_path = Path("nes-db/v2")
    db = FileDatabase(base_path=str(db_path))
    pub_service = PublicationService(database=db)
    search_service = SearchService(database=db)
    
    print("=" * 70)
    print("Relationship Creation Example - Political Party Memberships")
    print("=" * 70)
    
    # Define relationships to create
    relationships_to_create = [
        {
            "source": "entity:person/pushpa-kamal-dahal",
            "target": "entity:organization/political_party/nepal-communist-party-maoist-centre",
            "type": "MEMBER_OF",
            "start_date": date(1994, 1, 1),
            "attributes": {
                "role": "Chairman",
                "founding_member": True
            },
            "description": "Pushpa Kamal Dahal (Prachanda) is the founding chairman of CPN Maoist Centre"
        },
        {
            "source": "entity:person/sher-bahadur-deuba",
            "target": "entity:organization/political_party/nepali-congress",
            "type": "MEMBER_OF",
            "start_date": date(1971, 1, 1),
            "attributes": {
                "role": "President",
                "senior_leader": True
            },
            "description": "Sher Bahadur Deuba is the president of Nepali Congress"
        },
        {
            "source": "entity:person/khadga-prasad-oli",
            "target": "entity:organization/political_party/cpn-uml",
            "type": "MEMBER_OF",
            "start_date": date(1991, 1, 1),
            "attributes": {
                "role": "Chairman",
                "senior_leader": True
            },
            "description": "KP Sharma Oli is the chairman of CPN-UML"
        },
        {
            "source": "entity:person/ram-chandra-poudel",
            "target": "entity:organization/political_party/nepali-congress",
            "type": "MEMBER_OF",
            "start_date": date(1970, 1, 1),
            "attributes": {
                "role": "Senior Leader",
                "former_positions": ["Acting President", "General Secretary"]
            },
            "description": "Ram Chandra Poudel is a senior leader of Nepali Congress"
        }
    ]
    
    # Step 1: Create relationships
    print("\n1. Creating political party membership relationships...")
    created_relationships = []
    
    for rel_data in relationships_to_create:
        # Verify entities exist
        source_entity = await pub_service.get_entity(rel_data["source"])
        target_entity = await pub_service.get_entity(rel_data["target"])
        
        if not source_entity:
            print(f"   ⚠ Skipping: Source entity not found: {rel_data['source']}")
            continue
        
        if not target_entity:
            print(f"   ⚠ Skipping: Target entity not found: {rel_data['target']}")
            continue
        
        # Create the relationship
        try:
            relationship = await pub_service.create_relationship(
                source_entity_id=rel_data["source"],
                target_entity_id=rel_data["target"],
                relationship_type=rel_data["type"],
                start_date=rel_data.get("start_date"),
                end_date=rel_data.get("end_date"),
                attributes=rel_data.get("attributes"),
                author_id="author:human:data-maintainer",
                change_description=rel_data["description"]
            )
            
            created_relationships.append(relationship)
            
            print(f"   ✓ Created: {source_entity.names[0].en.full} → {target_entity.names[0].en.full}")
            print(f"     Type: {relationship.type}")
            print(f"     ID: {relationship.id}")
            
        except Exception as e:
            print(f"   ❌ Failed to create relationship: {e}")
    
    print(f"\n   Total relationships created: {len(created_relationships)}")
    
    # Step 2: Query relationships for a specific entity
    print("\n2. Querying relationships for Ram Chandra Poudel...")
    entity_id = "entity:person/ram-chandra-poudel"
    
    relationships = await search_service.search_relationships(
        source_entity_id=entity_id,
        limit=10
    )
    
    if relationships:
        print(f"   Found {len(relationships)} relationship(s):")
        for rel in relationships:
            target = await pub_service.get_entity(rel.target_entity_id)
            if target:
                print(f"\n   - {rel.type} → {target.names[0].en.full}")
                print(f"     Since: {rel.start_date or 'Unknown'}")
                if rel.attributes:
                    print(f"     Role: {rel.attributes.get('role', 'Member')}")
    else:
        print("   No relationships found")
    
    # Step 3: Query all MEMBER_OF relationships
    print("\n3. Querying all MEMBER_OF relationships...")
    
    all_memberships = await search_service.search_relationships(
        relationship_type="MEMBER_OF",
        limit=20
    )
    
    print(f"   Found {len(all_memberships)} membership relationship(s):")
    
    for rel in all_memberships[:5]:  # Show first 5
        source = await pub_service.get_entity(rel.source_entity_id)
        target = await pub_service.get_entity(rel.target_entity_id)
        
        if source and target:
            print(f"\n   - {source.names[0].en.full}")
            print(f"     Member of: {target.names[0].en.full}")
            if rel.attributes and "role" in rel.attributes:
                print(f"     Role: {rel.attributes['role']}")
    
    # Step 4: Show relationship version history
    if created_relationships:
        print("\n4. Relationship version history (first relationship):")
        first_rel = created_relationships[0]
        
        versions = await pub_service.get_relationship_versions(first_rel.id)
        
        for version in versions:
            print(f"\n   Version {version.version_number}:")
            print(f"   - Created: {version.created_at}")
            print(f"   - Author: {version.author.slug}")
            print(f"   - Description: {version.change_description or '(no description)'}")
    
    print("\n" + "=" * 70)
    print("✓ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
