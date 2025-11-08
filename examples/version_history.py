"""Example: Explore version history and audit trails.

This example demonstrates how to:
1. View complete version history for an entity
2. Compare versions to see what changed
3. Retrieve specific historical versions
4. Track who made changes and when
5. Analyze change patterns over time

The example uses authentic Nepali politician data.
"""

import asyncio
from pathlib import Path
from datetime import datetime

from nes2.database.file_database import FileDatabase
from nes2.services.publication import PublicationService


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    if not dt:
        return "Unknown"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def compare_attributes(old_attrs: dict, new_attrs: dict) -> dict:
    """Compare two attribute dictionaries and return changes.
    
    Returns:
        Dictionary with 'added', 'removed', and 'modified' keys
    """
    changes = {
        "added": {},
        "removed": {},
        "modified": {}
    }
    
    old_attrs = old_attrs or {}
    new_attrs = new_attrs or {}
    
    # Find added and modified
    for key, new_value in new_attrs.items():
        if key not in old_attrs:
            changes["added"][key] = new_value
        elif old_attrs[key] != new_value:
            changes["modified"][key] = {
                "old": old_attrs[key],
                "new": new_value
            }
    
    # Find removed
    for key in old_attrs:
        if key not in new_attrs:
            changes["removed"][key] = old_attrs[key]
    
    return changes


async def display_version_details(version, version_number: int):
    """Display detailed information about a version."""
    print(f"\n{'─' * 70}")
    print(f"Version {version_number}")
    print(f"{'─' * 70}")
    
    print(f"Created: {format_datetime(version.created_at)}")
    print(f"Author: {version.author.slug}")
    
    if version.author.names:
        print(f"Author Name: {version.author.names[0].en.full}")
    
    print(f"Description: {version.change_description or '(no description)'}")
    
    # Display snapshot summary
    if version.snapshot:
        snapshot = version.snapshot
        
        print(f"\nSnapshot Summary:")
        print(f"  Type: {snapshot.get('type')}/{snapshot.get('sub_type', 'N/A')}")
        
        # Names
        if "names" in snapshot and snapshot["names"]:
            print(f"  Names: {len(snapshot['names'])} name(s)")
            for name in snapshot["names"][:2]:  # Show first 2
                print(f"    - {name.get('kind')}: {name.get('en', {}).get('full', 'N/A')}")
        
        # Attributes
        if "attributes" in snapshot and snapshot["attributes"]:
            print(f"  Attributes: {len(snapshot['attributes'])} attribute(s)")
            for key in list(snapshot["attributes"].keys())[:5]:  # Show first 5
                value = snapshot["attributes"][key]
                if isinstance(value, (list, dict)):
                    print(f"    - {key}: {type(value).__name__}")
                else:
                    print(f"    - {key}: {value}")


async def main():
    """Explore version history for a Nepali politician."""
    
    # Initialize database and publication service
    db_path = Path("nes-db/v2")
    db = FileDatabase(base_path=str(db_path))
    pub_service = PublicationService(database=db)
    
    print("=" * 70)
    print("Version History Example - Pushpa Kamal Dahal (Prachanda)")
    print("=" * 70)
    
    # Entity ID for Pushpa Kamal Dahal
    entity_id = "entity:person/pushpa-kamal-dahal"
    
    # Step 1: Get current entity
    print(f"\n1. Current entity state:")
    entity = await pub_service.get_entity(entity_id)
    
    if not entity:
        print(f"   ❌ Entity not found: {entity_id}")
        print("   Please ensure the entity exists in the database first.")
        return
    
    print(f"   Name: {entity.names[0].en.full} / {entity.names[0].ne.full}")
    print(f"   Current Version: {entity.version_summary.version_number}")
    print(f"   Last Updated: {format_datetime(entity.version_summary.created_at)}")
    print(f"   Last Updated By: {entity.version_summary.author.slug}")
    
    # Step 2: Retrieve complete version history
    print(f"\n2. Retrieving version history...")
    versions = await pub_service.get_entity_versions(entity_id)
    
    print(f"   Total versions: {len(versions)}")
    
    if not versions:
        print("   No version history available")
        return
    
    # Step 3: Display version timeline
    print(f"\n3. Version timeline:")
    print(f"\n   {'Ver':<5} {'Date':<20} {'Author':<30} {'Description':<30}")
    print(f"   {'-' * 85}")
    
    for version in versions:
        date_str = format_datetime(version.created_at)[:19]
        author_str = version.author.slug[:28]
        desc_str = (version.change_description or "")[:28]
        
        print(f"   {version.version_number:<5} {date_str:<20} {author_str:<30} {desc_str:<30}")
    
    # Step 4: Display detailed information for each version
    print(f"\n4. Detailed version information:")
    
    for version in versions:
        await display_version_details(version, version.version_number)
    
    # Step 5: Compare consecutive versions
    print(f"\n5. Changes between versions:")
    
    for i in range(len(versions) - 1):
        current_version = versions[i]
        next_version = versions[i + 1]
        
        print(f"\n{'─' * 70}")
        print(f"Changes from Version {current_version.version_number} → {next_version.version_number}")
        print(f"{'─' * 70}")
        
        # Compare attributes
        old_attrs = current_version.snapshot.get("attributes", {})
        new_attrs = next_version.snapshot.get("attributes", {})
        
        changes = compare_attributes(old_attrs, new_attrs)
        
        if changes["added"]:
            print(f"\n  Added attributes:")
            for key, value in changes["added"].items():
                print(f"    + {key}: {value}")
        
        if changes["modified"]:
            print(f"\n  Modified attributes:")
            for key, change in changes["modified"].items():
                print(f"    ~ {key}:")
                print(f"      Old: {change['old']}")
                print(f"      New: {change['new']}")
        
        if changes["removed"]:
            print(f"\n  Removed attributes:")
            for key, value in changes["removed"].items():
                print(f"    - {key}: {value}")
        
        if not any([changes["added"], changes["modified"], changes["removed"]]):
            print(f"  (No attribute changes)")
    
    # Step 6: Retrieve a specific historical version
    print(f"\n6. Retrieving specific historical version:")
    
    if len(versions) >= 2:
        # Get version 1 (the original)
        version_1 = versions[0]
        
        print(f"\n   Version 1 (Original):")
        print(f"   Created: {format_datetime(version_1.created_at)}")
        print(f"   Author: {version_1.author.slug}")
        
        if version_1.snapshot:
            snapshot = version_1.snapshot
            
            print(f"\n   Original state:")
            if "names" in snapshot and snapshot["names"]:
                print(f"   Names:")
                for name in snapshot["names"]:
                    print(f"     - {name.get('kind')}: {name.get('en', {}).get('full', 'N/A')}")
            
            if "attributes" in snapshot and snapshot["attributes"]:
                print(f"\n   Attributes:")
                for key, value in snapshot["attributes"].items():
                    print(f"     - {key}: {value}")
    
    # Step 7: Analyze change patterns
    print(f"\n7. Change pattern analysis:")
    
    # Count changes by author
    author_changes = {}
    for version in versions:
        author_slug = version.author.slug
        author_changes[author_slug] = author_changes.get(author_slug, 0) + 1
    
    print(f"\n   Changes by author:")
    for author, count in sorted(author_changes.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {author}: {count} change(s)")
    
    # Time between changes
    if len(versions) >= 2:
        print(f"\n   Time between changes:")
        for i in range(len(versions) - 1):
            current = versions[i]
            next_ver = versions[i + 1]
            
            if current.created_at and next_ver.created_at:
                time_diff = next_ver.created_at - current.created_at
                days = time_diff.days
                hours = time_diff.seconds // 3600
                
                print(f"   - V{current.version_number} → V{next_ver.version_number}: {days} days, {hours} hours")
    
    print("\n" + "=" * 70)
    print("✓ Version history exploration completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
