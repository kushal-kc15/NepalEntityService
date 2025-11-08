"""Example: Batch import multiple entities with automatic versioning.

This example demonstrates how to:
1. Import multiple entities in a batch operation
2. Handle errors gracefully during batch import
3. Track import statistics
4. Create relationships between imported entities
5. Validate imported data

The example imports authentic Nepali political party data.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any

from nes2.database.file_database import FileDatabase
from nes2.services.publication import PublicationService


# Sample data: Nepali political parties
POLITICAL_PARTIES = [
    {
        "slug": "nepali-congress",
        "type": "organization",
        "sub_type": "political_party",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": "Nepali Congress"},
                "ne": {"full": "नेपाली कांग्रेस"}
            },
            {
                "kind": "ALIAS",
                "en": {"full": "NC"},
                "ne": {"full": "ने.कां."}
            }
        ],
        "attributes": {
            "founded": "1947",
            "ideology": ["Social Democracy", "Democratic Socialism"],
            "headquarters": "Sanepa, Lalitpur",
            "symbol": "Tree"
        }
    },
    {
        "slug": "cpn-uml",
        "type": "organization",
        "sub_type": "political_party",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": "Communist Party of Nepal (Unified Marxist-Leninist)"},
                "ne": {"full": "नेपाल कम्युनिष्ट पार्टी (एकीकृत मार्क्सवादी-लेनिनवादी)"}
            },
            {
                "kind": "ALIAS",
                "en": {"full": "CPN-UML"},
                "ne": {"full": "ने.क.पा. (एमाले)"}
            }
        ],
        "attributes": {
            "founded": "1991",
            "ideology": ["Communism", "Marxism-Leninism"],
            "headquarters": "Dhumbarahi, Kathmandu",
            "symbol": "Sun"
        }
    },
    {
        "slug": "nepal-communist-party-maoist-centre",
        "type": "organization",
        "sub_type": "political_party",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": "Communist Party of Nepal (Maoist Centre)"},
                "ne": {"full": "नेपाल कम्युनिष्ट पार्टी (माओवादी केन्द्र)"}
            },
            {
                "kind": "ALIAS",
                "en": {"full": "CPN-MC"},
                "ne": {"full": "ने.क.पा. (माओवादी केन्द्र)"}
            }
        ],
        "attributes": {
            "founded": "2009",
            "ideology": ["Maoism", "Communism"],
            "headquarters": "Paris Danda, Kathmandu",
            "symbol": "Hammer and Sickle"
        }
    },
    {
        "slug": "rastriya-swatantra-party",
        "type": "organization",
        "sub_type": "political_party",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": "Rastriya Swatantra Party"},
                "ne": {"full": "राष्ट्रिय स्वतन्त्र पार्टी"}
            },
            {
                "kind": "ALIAS",
                "en": {"full": "RSP"},
                "ne": {"full": "रा.स्व.पा."}
            }
        ],
        "attributes": {
            "founded": "2022",
            "ideology": ["Good Governance", "Anti-Corruption"],
            "headquarters": "Kathmandu",
            "symbol": "Bell"
        }
    },
    {
        "slug": "nepal-samajbadi-party",
        "type": "organization",
        "sub_type": "political_party",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": "Nepal Samajbadi Party"},
                "ne": {"full": "नेपाल समाजवादी पार्टी"}
            },
            {
                "kind": "ALIAS",
                "en": {"full": "NSP"},
                "ne": {"full": "ने.स.पा."}
            }
        ],
        "attributes": {
            "founded": "2020",
            "ideology": ["Socialism", "Federalism"],
            "headquarters": "Kathmandu",
            "symbol": "Plough"
        }
    }
]


async def batch_import_entities(
    pub_service: PublicationService,
    entities_data: List[Dict[str, Any]],
    author_id: str
) -> Dict[str, Any]:
    """Import multiple entities in a batch operation.
    
    Args:
        pub_service: Publication service instance
        entities_data: List of entity data dictionaries
        author_id: Author performing the import
        
    Returns:
        Dictionary with import statistics
    """
    stats = {
        "total": len(entities_data),
        "created": 0,
        "updated": 0,
        "failed": 0,
        "errors": []
    }
    
    for entity_data in entities_data:
        try:
            # Check if entity already exists
            from nes2.core.identifiers import build_entity_id
            entity_id = build_entity_id(
                entity_data["type"],
                entity_data.get("sub_type"),
                entity_data["slug"]
            )
            
            existing = await pub_service.get_entity(entity_id)
            
            if existing:
                # Update existing entity
                # Merge attributes
                if "attributes" in entity_data:
                    if not existing.attributes:
                        existing.attributes = {}
                    existing.attributes.update(entity_data["attributes"])
                
                await pub_service.update_entity(
                    entity=existing,
                    author_id=author_id,
                    change_description=f"Batch import update: {entity_data['slug']}"
                )
                stats["updated"] += 1
                print(f"   ✓ Updated: {entity_data['slug']}")
            else:
                # Create new entity
                await pub_service.create_entity(
                    entity_data=entity_data,
                    author_id=author_id,
                    change_description=f"Batch import: {entity_data['slug']}"
                )
                stats["created"] += 1
                print(f"   ✓ Created: {entity_data['slug']}")
                
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append({
                "slug": entity_data.get("slug", "unknown"),
                "error": str(e)
            })
            print(f"   ❌ Failed: {entity_data.get('slug', 'unknown')} - {e}")
    
    return stats


async def main():
    """Batch import Nepali political parties."""
    
    # Initialize database and publication service
    db_path = Path("nes-db/v2")
    db = FileDatabase(base_path=str(db_path))
    pub_service = PublicationService(database=db)
    
    print("=" * 70)
    print("Batch Import Example - Nepali Political Parties")
    print("=" * 70)
    
    # Step 1: Display import plan
    print(f"\n1. Import plan:")
    print(f"   Total entities to import: {len(POLITICAL_PARTIES)}")
    print(f"   Entity type: Political Parties")
    print(f"   Author: author:system:batch-importer")
    
    print("\n   Entities to import:")
    for party in POLITICAL_PARTIES:
        print(f"   - {party['names'][0]['en']['full']} ({party['slug']})")
    
    # Step 2: Perform batch import
    print(f"\n2. Importing entities...")
    
    stats = await batch_import_entities(
        pub_service=pub_service,
        entities_data=POLITICAL_PARTIES,
        author_id="author:system:batch-importer"
    )
    
    # Step 3: Display import statistics
    print(f"\n3. Import statistics:")
    print(f"   Total processed: {stats['total']}")
    print(f"   Created: {stats['created']}")
    print(f"   Updated: {stats['updated']}")
    print(f"   Failed: {stats['failed']}")
    
    if stats["errors"]:
        print(f"\n   Errors:")
        for error in stats["errors"]:
            print(f"   - {error['slug']}: {error['error']}")
    
    # Step 4: Verify imported entities
    print(f"\n4. Verifying imported entities...")
    
    for party_data in POLITICAL_PARTIES:
        from nes2.core.identifiers import build_entity_id
        entity_id = build_entity_id(
            party_data["type"],
            party_data.get("sub_type"),
            party_data["slug"]
        )
        
        entity = await pub_service.get_entity(entity_id)
        
        if entity:
            print(f"\n   ✓ {entity.names[0].en.full}")
            print(f"     ID: {entity.id}")
            print(f"     Version: {entity.version_summary.version_number}")
            print(f"     Founded: {entity.attributes.get('founded', 'Unknown')}")
            print(f"     Headquarters: {entity.attributes.get('headquarters', 'Unknown')}")
        else:
            print(f"\n   ❌ Not found: {party_data['slug']}")
    
    # Step 5: Show sample entity details
    print(f"\n5. Sample entity details (Nepali Congress):")
    
    nc_id = "entity:organization/political_party/nepali-congress"
    nc_entity = await pub_service.get_entity(nc_id)
    
    if nc_entity:
        print(f"\n   Names:")
        for name in nc_entity.names:
            print(f"   - {name.kind}: {name.en.full} / {name.ne.full}")
        
        print(f"\n   Attributes:")
        for key, value in nc_entity.attributes.items():
            print(f"   - {key}: {value}")
        
        print(f"\n   Version Info:")
        print(f"   - Version: {nc_entity.version_summary.version_number}")
        print(f"   - Created: {nc_entity.version_summary.created_at}")
        print(f"   - Author: {nc_entity.version_summary.author.slug}")
    
    print("\n" + "=" * 70)
    print("✓ Batch import completed successfully!")
    print(f"  {stats['created']} created, {stats['updated']} updated, {stats['failed']} failed")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
