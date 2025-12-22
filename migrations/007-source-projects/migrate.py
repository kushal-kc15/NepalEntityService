"""
Migration: 007-source-projects
Description: Import development projects for Nepal from multiple sources:
  - MoF DFMIS (primary source - Nepal's official aid management system)
  - World Bank (secondary - skip duplicates)
  - Asian Development Bank (secondary - skip duplicates)
  - JICA (secondary - skip duplicates)

Author: Nepal Development Project Team
Date: 2025-01-26
"""

import html
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add migration directory to path for local imports
_migration_dir = Path(__file__).parent
if str(_migration_dir) not in sys.path:
    sys.path.insert(0, str(_migration_dir))

from project_matcher import (  # noqa: E402
    ADBMatcher,
    JICAMatcher,
    MatchLevel,
    ProjectMatcher,
    WorldBankMatcher,
)

from nes.core.models import (  # noqa: E402
    Address,
    Attribution,
    ExternalIdentifier,
    LangText,
    LangTextValue,
    Name,
    NameParts,
)
from nes.core.models.base import NameKind  # noqa: E402
from nes.core.models.entity import EntitySubType, EntityType  # noqa: E402
from nes.core.models.version import Author  # noqa: E402
from nes.core.utils.slug_helper import text_to_slug  # noqa: E402
from nes.services.migration.context import MigrationContext  # noqa: E402
from nes.services.scraping.normalization import NameExtractor  # noqa: E402

# Migration metadata
AUTHOR = "Nava Yuwa Central"
DATE = "2025-01-26"
DESCRIPTION = "Import development projects for Nepal from multiple sources"
CHANGE_DESCRIPTION = "Initial sourcing from MoF DFMIS API"

name_extractor = NameExtractor()


class _HTMLStripper(HTMLParser):
    """Simple HTML tag stripper for converting HTML content to plain text."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


def _parse_date(date_input):
    """Parse date from various formats and return a date object."""
    if not date_input:
        return None

    try:
        if isinstance(date_input, str):
            # Replace 'Z' with '+00:00' for proper ISO format parsing
            iso_date = date_input.replace("Z", "+00:00")
            return datetime.fromisoformat(iso_date).date()
        elif hasattr(date_input, "date"):  # datetime object
            return date_input.date()
        else:
            return date_input
    except Exception:
        return None


def _strip_html_tags(text: str) -> str:
    """Strip HTML tags from text content and return plain text."""
    if not text:
        return text

    unescaped = html.unescape(text)
    stripper = _HTMLStripper()
    stripper.feed(unescaped)
    return stripper.get_data().strip()


def _normalize_location_name(name: str) -> str:
    """Normalize location name for matching."""
    s = (name or "").strip().lower()
    if not s:
        return s
    s = s.replace(",", " ")
    s = " ".join(s.split())
    suffixes = [
        "province",
        "pradesh",
        "प्रदेश",
        "district",
        "जिल्ला",
        "metropolitan city",
        "महानगरपालिका",
        "sub metropolitan city",
        "sub-metropolitan city",
        "उपमहानगरपालिका",
        "municipality",
        "नगरपालिका",
        "rural municipality",
        "गाउँपालिका",
    ]
    for suffix in suffixes:
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
            s = " ".join(s.split())
    return s


# Location name aliases for common misspellings
LOCATION_NAME_ALIASES = {
    "sankhuwasava": "sankhuwasabha",
    "panchthar": "pachthar",
    "madesh": "madhesh",
    "sidhupalchowk": "sindhupalchok",
    "kavrepalanchowk": "kavrepalanchok",
    "makawanpur": "makwanpur",
    "chitawan": "chitwan",
    "parbat": "parwat",
    "rukumkot": "eastern rukum",
    "arghakhachi": "arghakhanchi",
    "nawalparasi": "nawalpur",
    "rukum": "western rukum",
    "sudurpashchim": "sudur paschimanchal",
    "achham": "acham",
}


def _map_organization_subtype(
    architecture_name: str = "",
    group_name: str = "",
    org_name: str = "",
    is_donor: bool = False,
) -> EntitySubType:
    """
    Map DFMIS organization to appropriate entity subtypes.

    Uses three sources of information:
    1. architecture_name - from DFMIS raw_payload (most reliable for donors)
    2. group_name - from DFMIS raw_payload
    3. org_name - organization name (used for implementing/executing agencies)
    4. is_donor - whether this is a funding organization (affects default)

    Default behavior:
    - Donors without clear classification → INTERNATIONAL_ORG (foreign aid context)
    - Implementing/executing agencies without clear classification → NGO (local implementers)
    """
    arch_lower = (architecture_name or "").strip().lower()
    group_lower = (group_name or "").strip().lower()
    name_lower = (org_name or "").strip().lower()

    # 1. Check architecture name first (most reliable for donors)
    if "government of nepal" in arch_lower:
        return EntitySubType.GOVERNMENT_BODY

    if "non-government" in arch_lower or "non government" in arch_lower:
        if group_lower == "ngo":
            return EntitySubType.NGO
        elif group_lower == "ingo":
            return EntitySubType.INTERNATIONAL_ORG
        return EntitySubType.NGO

    if "multilateral" in arch_lower or "bilateral" in arch_lower:
        return EntitySubType.INTERNATIONAL_ORG

    # 2. Check group name
    if group_lower == "ngo":
        return EntitySubType.NGO
    if group_lower == "ingo":
        return EntitySubType.INTERNATIONAL_ORG
    if "line ministries" in group_lower:
        return EntitySubType.GOVERNMENT_BODY

    # 3. Name-based detection for implementing/executing agencies
    if name_lower:
        # Nepal government bodies
        gov_keywords = [
            "ministry of",
            "department of",
            "office of",
            "government of nepal",
            "nepal government",
            "commission",
            "secretariat",
            "authority",
            "council",
            "board",
            "bureau",
            # Nepali local government units
            "gaunpalika",
            "nagarpalika",
            "mahanagarpalika",
            "rural municipality",
            "municipality",
            "metropolitan",
            "district",
            "province",
            "pradesh",
        ]
        for kw in gov_keywords:
            if kw in name_lower:
                return EntitySubType.GOVERNMENT_BODY

        # International organizations / bilateral agencies
        intl_keywords = [
            "international",
            "world bank",
            "asian development",
            "united nations",
            "usaid",
            "jica",
            "dfid",
            "giz",
            "european union",
            "embassy",
            "cooperation agency",
            "development bank",
            "monetary fund",
        ]
        for kw in intl_keywords:
            if kw in name_lower:
                return EntitySubType.INTERNATIONAL_ORG

    # 4. Default based on role
    # Donors are typically international orgs (foreign aid)
    # Implementing/executing agencies are typically local NGOs
    if is_donor:
        return EntitySubType.INTERNATIONAL_ORG
    else:
        return EntitySubType.NGO


class ProjectMigration:
    """Migration class for development projects from multiple sources."""

    # Source configuration: (file_name, matcher_class, source_label, change_description)
    SOURCES = [
        ("dfmis_projects.jsonl", None, "DFMIS", "Initial sourcing from MoF DFMIS API"),
        (
            "world_bank_projects.jsonl",
            WorldBankMatcher,
            "World Bank",
            "Import from World Bank Projects API",
        ),
        (
            "adb_projects.jsonl",
            ADBMatcher,
            "ADB",
            "Import from ADB IATI XML Feed",
        ),
        (
            "jica_projects.jsonl",
            JICAMatcher,
            "JICA",
            "Import from JICA Yen Loan Database",
        ),
    ]

    def __init__(self, context: MigrationContext):
        self.context = context
        self.author_id: str = ""
        self.created_entity_ids: List[str] = []
        self.created_relationship_ids: List[str] = []
        self.organization_cache: Dict[str, str] = {}  # org_name -> entity_id
        self.location_lookup: Dict[str, Any] = {}
        self.province_lookup: Dict[str, Any] = {}
        self.district_lookup: Dict[str, Any] = {}
        self.municipality_lookup: Dict[str, Any] = {}
        # Track all migrated projects for deduplication (converted to matcher format)
        self.migrated_projects: List[Dict[str, Any]] = []

    async def run(self) -> None:
        """Run the migration for all sources."""
        self.context.log(
            "Migration started: Importing development projects from multiple sources"
        )

        try:
            await self._setup_author()
            await self._build_location_lookups()
            await self._build_organization_cache()

            # Process each source in order
            total_created = 0
            total_skipped = 0
            total_relationships = 0

            for source_file, matcher_class, source_label, change_desc in self.SOURCES:
                self.context.log(f"\n{'='*60}")
                self.context.log(f"Processing source: {source_label}")
                self.context.log(f"{'='*60}")

                # Load projects for this source
                projects = self._load_projects_from_file(source_file)
                if not projects:
                    self.context.log(f"  No projects found in {source_file}, skipping")
                    continue

                # Extract and create organizations
                org_data = self._extract_organizations_from_projects(projects)
                self._validate_organization_slugs(org_data)
                await self._create_organizations(org_data)

                # Apply deduplication for secondary sources
                if matcher_class is not None:
                    projects, skipped = self._filter_duplicates(
                        projects, matcher_class, source_label
                    )
                    total_skipped += skipped

                # Migrate projects
                created, rel_count = await self._migrate_projects(
                    projects, source_label, change_desc
                )
                total_created += created
                total_relationships += rel_count

            await self._verify()
            self.context.log(f"\n{'='*60}")
            self.context.log("MIGRATION SUMMARY")
            self.context.log(f"{'='*60}")
            self.context.log(f"Total projects created: {total_created}")
            self.context.log(f"Total projects skipped (duplicates): {total_skipped}")
            self.context.log(f"Total relationships created: {total_relationships}")
            self.context.log("Migration completed successfully")
        except Exception as e:
            self.context.log(f"Migration failed: {e}")
            await self._rollback()
            raise

    def _load_projects_from_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load projects from a JSONL file in the source directory."""
        projects = []
        source_file = self.context.migration_dir / "source" / filename
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        projects.append(json.loads(line))
            self.context.log(
                f"  Loaded {len(projects)} projects from source/{filename}"
            )
        except FileNotFoundError:
            self.context.log(f"  WARNING: source/{filename} not found")
            return []

        return projects

    def _filter_duplicates(
        self,
        projects: List[Dict[str, Any]],
        matcher_class: type,
        source_label: str,
    ) -> tuple:
        """Filter out duplicate projects using the appropriate matcher.

        Args:
            projects: List of projects to filter
            matcher_class: Matcher class to use (WorldBankMatcher, ADBMatcher, etc.)
            source_label: Label for logging

        Returns:
            Tuple of (filtered_projects, skipped_count)
        """
        if not self.migrated_projects:
            self.context.log(f"  No existing projects to match against, importing all")
            return projects, 0

        # Create matcher with existing projects
        matcher = matcher_class(self.migrated_projects)

        filtered = []
        skipped = 0
        skip_reasons = {
            MatchLevel.HIGH_ID: 0,
            MatchLevel.HIGH_NAME: 0,
            MatchLevel.MEDIUM: 0,
            MatchLevel.LOW: 0,
        }

        for project in projects:
            result = matcher.find_match(project)
            if result.should_skip():
                skipped += 1
                skip_reasons[result.level] += 1
            else:
                filtered.append(project)

        # Log deduplication results
        self.context.log(f"  Deduplication results for {source_label}:")
        self.context.log(
            f"    - ID matches (skip):        {skip_reasons[MatchLevel.HIGH_ID]}"
        )
        self.context.log(
            f"    - Exact name (skip):        {skip_reasons[MatchLevel.HIGH_NAME]}"
        )
        self.context.log(
            f"    - Fuzzy + amount (skip):    {skip_reasons[MatchLevel.MEDIUM]}"
        )
        self.context.log(
            f"    - Fuzzy name only (skip):   {skip_reasons[MatchLevel.LOW]}"
        )
        self.context.log(f"    - No match (import):        {len(filtered)}")
        self.context.log(
            f"  Total: {len(projects)} -> {len(filtered)} after deduplication"
        )

        return filtered, skipped

    def _convert_to_matcher_format(
        self, project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert project data to format expected by matchers.

        Matchers expect: names[], total_commitment, financing[], donor_extensions[]
        """
        # Already in correct format from scrapers
        return project_data

    async def _setup_author(self) -> None:
        """Create the migration author."""
        author = Author(slug=text_to_slug(AUTHOR), name=AUTHOR)
        await self.context.db.put_author(author)
        self.author_id = author.id
        self.context.log(f"Created author: {author.name} ({self.author_id})")

    async def _build_location_lookups(self) -> None:
        """Build lookup dictionaries for locations."""
        locations = await self.context.search.search_entities(
            entity_type="location", limit=10_000
        )

        for loc in locations:
            st = loc.sub_type.value if loc.sub_type else None
            for nm in loc.names:
                if nm.en and nm.en.full:
                    key_full = nm.en.full.strip().lower()
                    key_norm = _normalize_location_name(nm.en.full)
                    self.location_lookup[key_full] = loc
                    self.location_lookup[key_norm] = loc
                    if st == "province":
                        self.province_lookup[key_full] = loc
                        self.province_lookup[key_norm] = loc
                    elif st == "district":
                        self.district_lookup[key_full] = loc
                        self.district_lookup[key_norm] = loc
                    elif st in [
                        "metropolitan_city",
                        "sub_metropolitan_city",
                        "municipality",
                        "rural_municipality",
                    ]:
                        self.municipality_lookup[key_full] = loc
                        self.municipality_lookup[key_norm] = loc
                if nm.ne and nm.ne.full:
                    key_ne = nm.ne.full.strip().lower()
                    key_ne_norm = _normalize_location_name(nm.ne.full)
                    self.location_lookup[key_ne] = loc
                    self.location_lookup[key_ne_norm] = loc
                    if st == "province":
                        self.province_lookup[key_ne] = loc
                        self.province_lookup[key_ne_norm] = loc
                    elif st == "district":
                        self.district_lookup[key_ne] = loc
                        self.district_lookup[key_ne_norm] = loc
                    elif st in [
                        "metropolitan_city",
                        "sub_metropolitan_city",
                        "municipality",
                        "rural_municipality",
                    ]:
                        self.municipality_lookup[key_ne] = loc
                        self.municipality_lookup[key_ne_norm] = loc

        self.context.log(f"Built location lookups: {len(self.location_lookup)} entries")

    async def _build_organization_cache(self) -> None:
        """Build cache of existing organizations."""
        orgs = await self.context.db.list_entities(
            entity_type="organization", limit=10_000
        )
        for org in orgs:
            for name in org.names:
                if name.en and name.en.full:
                    key = name.en.full.strip().lower()
                    self.organization_cache[key] = org.id
                if name.ne and name.ne.full:
                    key = name.ne.full.strip().lower()
                    self.organization_cache[key] = org.id

        self.context.log(
            f"Built organization cache: {len(self.organization_cache)} entries"
        )

    def _load_projects(self) -> List[Dict[str, Any]]:
        """Load projects from the pre-transformed JSONL file (backward compatibility)."""
        return self._load_projects_from_file("dfmis_projects.jsonl")

    def _extract_organizations_from_projects(
        self, projects: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract all unique organizations from project data.

        Returns a dict mapping org_name (lowercase) to org metadata.
        """
        orgs: Dict[str, Dict[str, Any]] = {}

        for project_data in projects:
            migration_meta = project_data.get("_migration_metadata", {})

            # Extract from development_agencies (donors)
            for agency in migration_meta.get("development_agencies", []):
                if isinstance(agency, dict) and agency.get("name"):
                    name = agency["name"]
                    key = name.strip().lower()
                    if key not in orgs and key not in self.organization_cache:
                        orgs[key] = {
                            "name": name,
                            "architecture": agency.get("architecture", ""),
                            "group": agency.get("group", ""),
                            "is_donor": True,
                        }

            # Extract from implementing_agencies
            for agency in migration_meta.get("implementing_agencies", []):
                if isinstance(agency, dict) and agency.get("name"):
                    name = agency["name"]
                    key = name.strip().lower()
                    if key not in orgs and key not in self.organization_cache:
                        orgs[key] = {
                            "name": name,
                            "architecture": agency.get("architecture", ""),
                            "group": agency.get("group", ""),
                            "is_donor": False,
                        }

            # Extract from executing_agencies
            for agency in migration_meta.get("executing_agencies", []):
                if isinstance(agency, dict) and agency.get("name"):
                    name = agency["name"]
                    key = name.strip().lower()
                    if key not in orgs and key not in self.organization_cache:
                        orgs[key] = {
                            "name": name,
                            "architecture": agency.get("architecture", ""),
                            "group": agency.get("group", ""),
                            "is_donor": False,
                        }

            # Extract from government_agencies
            for agency in migration_meta.get("government_agencies", []):
                if isinstance(agency, dict) and agency.get("name"):
                    name = agency["name"]
                    key = name.strip().lower()
                    if key not in orgs and key not in self.organization_cache:
                        orgs[key] = {
                            "name": name,
                            "architecture": agency.get("architecture", ""),
                            "group": agency.get("group", ""),
                            "is_donor": False,
                        }

        self.context.log(f"Extracted {len(orgs)} unique organizations from projects")
        return orgs

    def _validate_organization_slugs(self, org_data: Dict[str, Dict[str, Any]]) -> None:
        """Validate organization slugs and detect collisions."""
        slug_to_orgs: Dict[str, List[str]] = {}

        for key, data in org_data.items():
            slug = text_to_slug(data["name"])
            if not slug or len(slug) < 3:
                slug = f"org-{hash(data['name']) % 100000}"
            if len(slug) > 100:
                slug = slug[:100]

            # Store slug for collision detection
            data["slug"] = slug

            if slug not in slug_to_orgs:
                slug_to_orgs[slug] = []
            slug_to_orgs[slug].append(data["name"])

        # Check for collisions
        collisions = {
            slug: names for slug, names in slug_to_orgs.items() if len(names) > 1
        }
        if collisions:
            self.context.log(f"WARNING: Found {len(collisions)} slug collisions:")
            for slug, names in collisions.items():
                self.context.log(f"  {slug}: {names}")
                # Resolve by appending hash suffix
                for i, name in enumerate(names[1:], start=2):
                    for key, data in org_data.items():
                        if data["name"] == name:
                            data["slug"] = f"{slug}-{i}"
                            self.context.log(f"    Resolved: {name} -> {data['slug']}")

    async def _create_organizations(self, org_data: Dict[str, Dict[str, Any]]) -> None:
        """Create all organizations in batch."""
        created_count = 0
        skipped_count = 0

        for key, data in org_data.items():
            # Determine subtype
            subtype = _map_organization_subtype(
                data.get("architecture", ""),
                data.get("group", ""),
                data["name"],
                data.get("is_donor", False),
            )

            slug = data["slug"]
            expected_id = f"entity:organization/{subtype.value}/{slug}"

            # Check if already exists
            existing = await self.context.db.get_entity(expected_id)
            if existing:
                self.organization_cache[key] = expected_id
                skipped_count += 1
                continue

            entity_data = {
                "slug": slug,
                "names": [
                    Name(
                        kind=NameKind.PRIMARY, en=NameParts(full=data["name"])
                    ).model_dump()
                ],
                "attributions": [
                    Attribution(
                        title=LangText(
                            en=LangTextValue(
                                value="MoF DFMIS Organization", provenance="human"
                            )
                        ),
                        details=LangText(
                            en=LangTextValue(
                                value=f"Organization from MoF DFMIS - {data.get('architecture') or 'Development Partner'}",
                                provenance="human",
                            )
                        ),
                    ).model_dump()
                ],
            }

            # Add attributes if available
            if data.get("architecture") or data.get("group"):
                entity_data["attributes"] = {}
                if data.get("architecture"):
                    entity_data["attributes"]["architecture"] = data["architecture"]
                if data.get("group"):
                    entity_data["attributes"]["group"] = data["group"]

            try:
                org_entity = await self.context.publication.create_entity(
                    entity_type=EntityType.ORGANIZATION,
                    entity_subtype=subtype,
                    entity_data=entity_data,
                    author_id=self.author_id,
                    change_description=f"Import organization from MoF DFMIS: {data['name']}",
                )
                self.organization_cache[key] = org_entity.id
                self.created_entity_ids.append(org_entity.id)
                created_count += 1
            except ValueError as e:
                self.context.log(f"  Error creating organization {data['name']}: {e}")
                raise

        self.context.log(
            f"Organizations: created {created_count}, skipped {skipped_count} existing"
        )

    async def _migrate_projects(
        self,
        projects: List[Dict[str, Any]],
        source_label: str = "DFMIS",
        change_description: str = CHANGE_DESCRIPTION,
    ) -> tuple:
        """Create project entities and relationships.

        Args:
            projects: List of project data to migrate
            source_label: Label for the source (DFMIS, World Bank, ADB, JICA)
            change_description: Description for version history

        Returns:
            Tuple of (created_count, relationship_count)
        """
        count = 0
        relationship_count = 0

        for project_data in projects:
            try:
                # Create project entity
                project_entity = await self._create_project_entity(
                    project_data, source_label, change_description
                )
                if not project_entity:
                    self.context.log(
                        f"  Warning: Failed to create project - missing slug or names: {project_data.get('slug', 'unknown')}"
                    )
                    continue

                self.created_entity_ids.append(project_entity.id)
                count += 1

                # Track for deduplication against future sources
                self.migrated_projects.append(project_data)

                # Create relationships
                rel_count = await self._create_project_relationships(
                    project_entity.id, project_data
                )
                relationship_count += rel_count

                if count % 100 == 0:
                    self.context.log(f"  Processed {count} {source_label} projects...")

            except Exception as e:
                self.context.log(
                    f"  Error processing project {project_data.get('slug', 'unknown')}: {e}"
                )
                raise

        self.context.log(f"  Created {count} {source_label} project entities")
        self.context.log(f"  Created {relationship_count} relationships")
        return count, relationship_count

    async def _create_project_entity(
        self,
        project_data: Dict[str, Any],
        source_label: str = "DFMIS",
        change_description: str = CHANGE_DESCRIPTION,
    ) -> Optional[Any]:
        """Create a project entity from the pre-transformed data.

        Args:
            project_data: Project data dictionary
            source_label: Label for the source (DFMIS, World Bank, ADB, JICA)
            change_description: Description for version history

        Returns:
            Created project entity or None if failed
        """
        slug = project_data.get("slug", "")
        if not slug:
            return None

        # Ensure slug is valid (lowercase, alphanumeric with hyphens only)
        slug = slug.lower()
        if len(slug) > 100:
            slug = slug[:100]
        if len(slug) < 3:
            slug = f"project-{int(datetime.now().timestamp())}"

        # Build names
        names_data = project_data.get("names", [])
        if not names_data:
            return None

        names = []
        for name_entry in names_data:
            name_obj = Name(
                kind=NameKind(name_entry.get("kind", "PRIMARY")),
                en=(
                    NameParts(full=name_entry.get("en", {}).get("full"))
                    if name_entry.get("en")
                    else None
                ),
                ne=(
                    NameParts(full=name_entry.get("ne", {}).get("full"))
                    if name_entry.get("ne")
                    else None
                ),
            )
            names.append(name_obj.model_dump())

        # Build description
        description = None
        desc_data = project_data.get("description")
        if desc_data:
            if isinstance(desc_data, dict):
                en_desc = desc_data.get("en", {})
                if en_desc and en_desc.get("value"):
                    clean_desc = _strip_html_tags(en_desc.get("value", ""))
                    if clean_desc:
                        description = LangText(
                            en=LangTextValue(
                                value=clean_desc[:5000], provenance="imported"
                            )
                        ).model_dump()
            elif isinstance(desc_data, str):
                # Handle string descriptions (from WB, ADB, JICA)
                clean_desc = _strip_html_tags(desc_data)
                if clean_desc:
                    description = LangText(
                        en=LangTextValue(value=clean_desc[:5000], provenance="imported")
                    ).model_dump()

        # Build attributions based on source
        attribution_title = source_label
        attribution_details = f"Imported from {source_label} on {DATE}"
        attributions = [
            Attribution(
                title=LangText(
                    en=LangTextValue(value=attribution_title, provenance="human")
                ),
                details=LangText(
                    en=LangTextValue(value=attribution_details, provenance="human")
                ),
            ).model_dump()
        ]

        # Build identifiers
        identifiers = []
        project_url = project_data.get("project_url")
        if project_url:
            # Extract project ID from slug
            project_id = slug
            for prefix in ["dfmis-", "wb-", "adb-", "jica-"]:
                if slug.startswith(prefix):
                    project_id = slug[len(prefix) :]
                    break
            identifiers.append(
                ExternalIdentifier(
                    scheme="other",
                    value=project_id,
                    url=str(project_url),
                    name=LangText(
                        en=LangTextValue(
                            value=f"{source_label} Project ID", provenance="human"
                        )
                    ),
                ).model_dump()
            )

        # Build entity data
        entity_data = {
            "slug": slug,
            "names": names,
            "attributions": attributions,
            "description": description,
            "identifiers": identifiers if identifiers else None,
            "stage": project_data.get("stage", "unknown"),
            "implementing_agency": project_data.get("implementing_agency"),
            "executing_agency": project_data.get("executing_agency"),
            "financing": project_data.get("financing"),
            "total_commitment": project_data.get("total_commitment"),
            "total_disbursement": project_data.get("total_disbursement"),
            "dates": project_data.get("dates"),
            "sectors": project_data.get("sectors"),
            "tags": project_data.get("tags"),
            "donor_extensions": project_data.get("donor_extensions"),
            "project_url": str(project_url) if project_url else None,
        }

        # Remove None values
        entity_data = {k: v for k, v in entity_data.items() if v is not None}

        # Check if entity already exists (e.g., from a previous partial run)
        expected_id = f"entity:project/development_project/{slug}"
        existing = await self.context.db.get_entity(expected_id)
        if existing:
            self.context.log(f"  Skipping existing project {expected_id}")
            return existing

        project = await self.context.publication.create_entity(
            entity_type=EntityType.PROJECT,
            entity_subtype=EntitySubType.DEVELOPMENT_PROJECT,
            entity_data=entity_data,
            author_id=self.author_id,
            change_description=change_description,
        )
        return project

    async def _create_project_relationships(
        self, project_id: str, project_data: Dict[str, Any]
    ) -> int:
        """Create relationships for a project entity using migration metadata."""
        rel_count = 0

        # Get migration metadata from transformed data (includes agency/location details)
        migration_meta = project_data.get("_migration_metadata", {})

        # Helper to create org relationship (orgs are pre-created in batch)
        async def create_org_relationship(
            agencies: List[Dict], rel_type: str, is_donor: bool
        ) -> int:
            count = 0
            for agency in agencies:
                if not isinstance(agency, dict):
                    continue
                org_name = agency.get("name", "")
                if not org_name:
                    continue
                org_id = self._get_organization_id(org_name)
                if org_id:
                    try:
                        rel = await self.context.publication.create_relationship(
                            source_entity_id=project_id,
                            target_entity_id=org_id,
                            relationship_type=rel_type,
                            author_id=self.author_id,
                            change_description=f"Project {rel_type.lower().replace('_', ' ')} {org_name}",
                        )
                        self.created_relationship_ids.append(rel.id)
                        count += 1
                    except Exception as e:
                        self.context.log(
                            f"  Warning: Could not create {rel_type} relationship: {type(e).__name__}: {e}"
                        )
            return count

        # Use migration metadata for relationships (has full org metadata)
        if migration_meta:
            # FUNDED_BY - from development_agencies (donors)
            dev_agencies = migration_meta.get("development_agencies", [])
            rel_count += await create_org_relationship(
                dev_agencies, "FUNDED_BY", is_donor=True
            )

            # IMPLEMENTED_BY - from implementing_agencies
            impl_agencies = migration_meta.get("implementing_agencies", [])
            rel_count += await create_org_relationship(
                impl_agencies, "IMPLEMENTED_BY", is_donor=False
            )

            # EXECUTED_BY - from executing_agencies
            exec_agencies = migration_meta.get("executing_agencies", [])
            rel_count += await create_org_relationship(
                exec_agencies, "EXECUTED_BY", is_donor=False
            )
        else:
            # Fallback to pre-transformed data (no org metadata, uses name heuristics)
            # FUNDED_BY from donor_extensions
            for donor_ext in project_data.get("donor_extensions", []):
                if not isinstance(donor_ext, dict):
                    continue
                donor_name = donor_ext.get("donor", "")
                if not donor_name:
                    continue
                org_id = self._get_organization_id(donor_name)
                if org_id:
                    try:
                        rel = await self.context.publication.create_relationship(
                            source_entity_id=project_id,
                            target_entity_id=org_id,
                            relationship_type="FUNDED_BY",
                            author_id=self.author_id,
                            change_description=f"Project funded by {donor_name}",
                        )
                        self.created_relationship_ids.append(rel.id)
                        rel_count += 1
                    except Exception as e:
                        self.context.log(
                            f"  Warning: Could not create FUNDED_BY relationship: {e}"
                        )

            # IMPLEMENTED_BY from implementing_agency string
            for agency_name in (
                project_data.get("implementing_agency", "") or ""
            ).split(","):
                agency_name = agency_name.strip()
                if not agency_name:
                    continue
                org_id = self._get_organization_id(agency_name)
                if org_id:
                    try:
                        rel = await self.context.publication.create_relationship(
                            source_entity_id=project_id,
                            target_entity_id=org_id,
                            relationship_type="IMPLEMENTED_BY",
                            author_id=self.author_id,
                            change_description=f"Project implemented by {agency_name}",
                        )
                        self.created_relationship_ids.append(rel.id)
                        rel_count += 1
                    except Exception as e:
                        self.context.log(
                            f"  Warning: Could not create IMPLEMENTED_BY relationship: {e}"
                        )

            # EXECUTED_BY from executing_agency string
            for agency_name in (project_data.get("executing_agency", "") or "").split(
                ","
            ):
                agency_name = agency_name.strip()
                if not agency_name:
                    continue
                org_id = self._get_organization_id(agency_name)
                if org_id:
                    try:
                        rel = await self.context.publication.create_relationship(
                            source_entity_id=project_id,
                            target_entity_id=org_id,
                            relationship_type="EXECUTED_BY",
                            author_id=self.author_id,
                            change_description=f"Project executed by {agency_name}",
                        )
                        self.created_relationship_ids.append(rel.id)
                        rel_count += 1
                    except Exception as e:
                        self.context.log(
                            f"  Warning: Could not create EXECUTED_BY relationship: {e}"
                        )

        # Create LOCATED_IN relationships from migration metadata
        if migration_meta:
            locations = migration_meta.get("locations", [])

            # Track which locations we've already linked to avoid duplicates
            linked_location_ids: Set[str] = set()

            for loc in locations:
                if not isinstance(loc, dict):
                    continue

                # Skip national level projects (no specific location)
                location_type = loc.get("location_type", "")
                if location_type == "National Level":
                    continue

                # Try to link to municipality first, then district, then province
                location_id = None
                location_name = None

                # Try municipality
                municipality_name = loc.get("municipality")
                if municipality_name:
                    location_id = self._find_location_id(
                        municipality_name, self.municipality_lookup
                    )
                    location_name = municipality_name

                # Try district if no municipality match
                if not location_id:
                    district_name = loc.get("district")
                    if district_name:
                        location_id = self._find_location_id(
                            district_name, self.district_lookup
                        )
                        location_name = district_name

                # Try province if no district match
                if not location_id:
                    province_name = loc.get("province")
                    if province_name:
                        location_id = self._find_location_id(
                            province_name, self.province_lookup
                        )
                        location_name = province_name

                # Create relationship if we found a matching location
                if location_id and location_id not in linked_location_ids:
                    try:
                        rel = await self.context.publication.create_relationship(
                            source_entity_id=project_id,
                            target_entity_id=location_id,
                            relationship_type="LOCATED_IN",
                            author_id=self.author_id,
                            change_description=f"Project located in {location_name}",
                        )
                        self.created_relationship_ids.append(rel.id)
                        linked_location_ids.add(location_id)
                        rel_count += 1
                    except Exception as e:
                        self.context.log(
                            f"  Warning: Could not create LOCATED_IN relationship for {location_name}: {e}"
                        )

        return rel_count

    def _find_location_id(
        self, location_name: str, lookup: Dict[str, Any]
    ) -> Optional[str]:
        """Find location ID from lookup dictionary."""
        if not location_name:
            return None

        # Try exact match first
        key_lower = location_name.strip().lower()
        if key_lower in lookup:
            return lookup[key_lower].id

        # Try normalized match
        key_norm = _normalize_location_name(location_name)
        if key_norm in lookup:
            return lookup[key_norm].id

        # Try with alias
        key_alias = LOCATION_NAME_ALIASES.get(key_norm, key_norm)
        if key_alias in lookup:
            return lookup[key_alias].id

        return None

    def _get_organization_id(self, org_name: str) -> Optional[str]:
        """Get organization ID from cache. Organizations are pre-created in batch."""
        if not org_name:
            return None

        cache_key = org_name.strip().lower()
        return self.organization_cache.get(cache_key)

    async def _verify(self) -> None:
        """Verify the migration results."""
        projects = await self.context.db.list_entities(
            limit=15_000, entity_type="project", sub_type="development_project"
        )
        self.context.log(f"Verified: {len(projects)} project entities in database")

    async def _rollback(self) -> None:
        """Rollback created entities and relationships on failure."""
        self.context.log("Rolling back migration...")

        # Delete relationships first
        for rel_id in reversed(self.created_relationship_ids):
            try:
                await self.context.publication.delete_relationship(
                    relationship_id=rel_id,
                    author_id=self.author_id,
                    change_description="Rollback: migration failed",
                )
                versions = await self.context.db.list_versions_by_entity(
                    entity_or_relationship_id=rel_id, limit=1000
                )
                for v in versions:
                    await self.context.db.delete_version(v.id)
            except Exception:
                pass

        # Delete entities
        for ent_id in reversed(self.created_entity_ids):
            try:
                await self.context.publication.delete_entity(
                    entity_id=ent_id,
                    author_id=self.author_id,
                    change_description="Rollback: migration failed",
                )
                versions = await self.context.db.list_versions_by_entity(
                    entity_or_relationship_id=ent_id, limit=1000
                )
                for v in versions:
                    await self.context.db.delete_version(v.id)
            except Exception:
                pass

        # Delete author
        try:
            await self.context.db.delete_author(self.author_id)
        except Exception:
            pass

        self.context.log("Rollback completed")


async def migrate(context: MigrationContext) -> None:
    """
    Import development projects for Nepal from multiple sources.

    Sources (in order of priority):
    1. MoF DFMIS (primary) - Nepal's official aid management system
    2. World Bank - skip duplicates found in DFMIS
    3. Asian Development Bank - skip duplicates found in DFMIS/WB
    4. JICA - skip duplicates found in DFMIS/WB/ADB

    Data sources:
    - DFMIS: dfims.mof.gov.np/api/v2/core/projects/
    - World Bank: search.worldbank.org/api/v3/projects
    - ADB: www.adb.org/iati/iati-activities-np.xml
    - JICA: JICA Yen Loan Database (CSV)
    """
    migration = ProjectMigration(context)
    await migration.run()
