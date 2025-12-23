# Migration 007: Import Development Projects

## Purpose

Import development project data from multiple sources into the Nepal Entity Service. This migration supports a multi-source architecture for aggregating project data from:

- **MoF DFMIS** (Ministry of Finance - Development Finance Information Management System) ✅ Primary source
- **World Bank** ✅ Implemented
- **Asian Development Bank (ADB)** ✅ Implemented
- **JICA** ✅ Implemented
- **NPC Project Bank** (planned)

## Data Sources

### MoF DFMIS (Primary Source)
- **API**: https://dfims.mof.gov.np/api/v2/core/projects/
- **Authority**: Ministry of Finance, Nepal
- **Data Type**: All development projects registered in Nepal's DFMIS system
- **Coverage**: 2,753 projects

### World Bank
- **API**: World Bank Projects API
- **Data Type**: World Bank-funded projects in Nepal
- **Coverage**: 279 projects (195 unique after deduplication)

### Asian Development Bank
- **API**: ADB IATI Data (https://data.adb.org/iati)
- **Data Type**: ADB-funded projects in Nepal
- **Coverage**: 118 projects (25 unique after deduplication)

### JICA
- **Source**: JICA Yen Loan data
- **Data Type**: Japanese ODA projects in Nepal
- **Coverage**: 15 projects (6 unique after deduplication)

## Two-Step Process

This migration uses a two-step approach for each data source:

### Step 1: Scrape Data

Run the scraping script for the desired source:

**MoF DFMIS:**
```bash
cd migrations/007-source-projects/mof_dfmis
poetry run python scrape_mof_dfmis.py
```

This will:
1. Fetch all projects from the DFMIS API (with caching to `all_projects.json`)
2. Normalize data to the standard Project model
3. Save transformed data to `source/dfmis_projects.jsonl`

### Step 2: Run Migration

After scraping, run the migration to import the data:

```bash
poetry run nes migration run 007-source-projects
```

## Deduplication Strategy

Since DFMIS is the authoritative source for Nepal's development projects, secondary sources (World Bank, ADB, JICA) are deduplicated against DFMIS to avoid creating duplicate project entries.

### ProjectMatcher Classes

The `project_matcher.py` module provides source-specific matchers:

```python
from project_matcher import WorldBankMatcher, ADBMatcher, JICAMatcher

# Each matcher knows how to identify its donor in DFMIS data
class WorldBankMatcher(ProjectMatcher):
    SOURCE = "WB"
    DONOR_NAMES = ["world bank", "ibrd", "ida", "international development association"]
```

### Match Levels (Conservative Approach)

Matches are categorized by confidence level:

| Level | Criteria | Action |
|-------|----------|--------|
| `ID_MATCH` | Donor project ID found in DFMIS identifiers | Skip (definite duplicate) |
| `EXACT_NAME` | Exact name match + same donor | Skip (definite duplicate) |
| `FUZZY_AMOUNT` | Fuzzy name (>85%) + similar amount (±20%) | Skip (likely duplicate) |
| `FUZZY_ONLY` | Fuzzy name match only | Skip (possible duplicate) |
| `NO_MATCH` | No match found | Import as new project |

### Processing Order

Sources are processed in priority order:

```python
SOURCES = [
    ("dfmis_projects.jsonl", None, "DFMIS"),           # Primary - no dedup
    ("world_bank_projects.jsonl", WorldBankMatcher, "World Bank"),
    ("adb_projects.jsonl", ADBMatcher, "ADB"),
    ("jica_projects.jsonl", JICAMatcher, "JICA"),
]
```

### Deduplication Results (Current)

| Source | Total | Imported | Skipped | Skip Rate |
|--------|-------|----------|---------|-----------|
| DFMIS | 2,753 | 2,753 | 0 | 0% |
| World Bank | 279 | 195 | 84 | 30% |
| ADB | 118 | 25 | 93 | 79% |
| JICA | 15 | 6 | 9 | 60% |

## What Gets Created

### Project Entities
- Bilingual names (English and Nepali where available)
- External identifiers (source project IDs)
- Project stage (pipeline, planning, approved, ongoing, completed, etc.)
- Financing components (loans, grants, mixed)
- Date events (approval, start, completion)
- Sector mappings
- Donor information

### Organization Entities (auto-created)
- Development agencies (donors)
- Implementing agencies
- Executing agencies
- Classified by subtype: `government_body`, `international_org`, `ngo`

### Relationships
- `FUNDED_BY`: Project → Donor organization
- `IMPLEMENTED_BY`: Project → Implementing agency
- `EXECUTED_BY`: Project → Executing agency
- `LOCATED_IN`: Project → Location (province/district/municipality)

## Data Normalization

The migration performs the following normalization:

1. **Project Stage**: Maps source-specific statuses to standard stages
2. **Organizations**: Auto-classifies by architecture (Government, Multilateral, Bilateral, NGO, INGO)
3. **Locations**: Links to existing location entities using fuzzy matching
4. **Financing**: Normalizes to grant/loan/mixed instrument types
5. **Dates**: Extracts approval, effectiveness, and completion dates

## Project Model

The `Project` entity extends the base `Entity` model with:

```python
class Project(Entity):
    type: Literal["project"]
    sub_type: EntitySubType = DEVELOPMENT_PROJECT
    stage: ProjectStage
    implementing_agency: Optional[str]
    executing_agency: Optional[str]
    financing: Optional[List[FinancingComponent]]
    dates: Optional[List[ProjectDateEvent]]
    locations: Optional[List[ProjectLocation]]
    sectors: Optional[List[SectorMapping]]
    tags: Optional[List[CrossCuttingTag]]
    donors: Optional[List[str]]
    donor_extensions: Optional[List[DonorExtension]]
    project_url: Optional[AnyUrl]
```

## File Structure

```
migrations/007-source-projects/
├── migrate.py                  # Main migration script
├── project_matcher.py          # Deduplication matchers
├── README.md                   # This file
├── mof_dfmis/
│   ├── scrape_mof_dfmis.py     # DFMIS scraper
│   └── all_projects.json       # Raw API cache
├── world_bank/
│   ├── scrape_world_bank.py    # World Bank scraper
│   └── check_wb_dfmis_overlap.py
├── asian_development_bank/
│   ├── scrape_adb.py           # ADB IATI scraper
│   └── check_adb_dfmis_overlap.py
├── jica/
│   ├── scrape_jica.py          # JICA scraper
│   ├── check_jica_dfmis_overlap.py
│   └── yen_loan.csv            # Source data
└── source/
    ├── dfmis_projects.jsonl
    ├── world_bank_projects.jsonl
    ├── adb_projects.jsonl
    └── jica_projects.jsonl
```

## Adding New Sources

To add a new data source:

1. Create a new folder: `migrations/007-source-projects/<source_name>/`
2. Create a scraper: `scrape_<source_name>.py`
3. Output to: `source/<source_name>_projects.jsonl`
4. Update `migrate.py` to load from the new source file
5. Add source-specific normalization logic

### Scraper Template

```python
async def scrape_and_save_projects(output_file: str = "<source>_projects.jsonl") -> int:
    """Scrape projects and save to JSONL file."""
    # 1. Fetch from API
    # 2. Normalize to Project model
    # 3. Add _migration_metadata for relationships
    # 4. Save to source/ directory
```

## Testing

After running the migration:

### Search for projects

```bash
nes search entities --type project --subtype development_project --limit 3
```

Example output:
```
Found 3 entities:

entity:project/development_project/dfmis-1317
  Name: Japanese FoodAid(KR)-2017
  Type: project/EntitySubType.DEVELOPMENT_PROJECT
  Version: 1

entity:project/development_project/dfmis-559
  Name: Rural Community Infrastructure Development Programme/Works
  Type: project/EntitySubType.DEVELOPMENT_PROJECT
  Version: 1

entity:project/development_project/dfmis-2184
  Name: Women and Girls' Leadership and Voice (LEAD)
  Type: project/EntitySubType.DEVELOPMENT_PROJECT
  Version: 1
```

### View a project

```bash
nes show entity:project/development_project/dfmis-1234
```

Example output:
```
Entity: entity:project/development_project/dfmis-1234
Type: project/EntitySubType.DEVELOPMENT_PROJECT
Slug: dfmis-1234

Names:
  PRIMARY:
    English: Pasang Lhamu-Nicole Niquille Hospital, Lukla

Identifiers:
  IdentifierScheme.OTHER: 1234

Version: 1
Created: 2025-12-15 12:08:37.515523+00:00
Author: nava-yuwa-central
```

### Check relationships for a project

```bash
nes search relationships --source entity:project/development_project/dfmis-1234
```

Example output:
```
Found 4 relationships:

relationship:...:FUNDED_BY
  Type: FUNDED_BY
  Source: entity:project/development_project/dfmis-1234
  Target: entity:organization/international_org/foundation-nicole-niquille-hospital-lukla

relationship:...:IMPLEMENTED_BY
  Type: IMPLEMENTED_BY
  Source: entity:project/development_project/dfmis-1234
  Target: entity:organization/ngo/pasang-lhamu-mountaineering-foundation

relationship:...:EXECUTED_BY
  Type: EXECUTED_BY
  Source: entity:project/development_project/dfmis-1234
  Target: entity:organization/international_org/foundation-nicole-niquille-hospital-lukla

relationship:...:LOCATED_IN
  Type: LOCATED_IN
  Source: entity:project/development_project/dfmis-1234
  Target: entity:location/district/solukhumbu
```

## Statistics (Current)

| Source | Projects | Organizations | Relationships |
|--------|----------|---------------|---------------|
| DFMIS | 2,753 | 583 | 17,528 |
| World Bank | 195 | 55 | 235 |
| ADB | 25 | 0 | 0 |
| JICA | 6 | 0 | 0 |
| **Total** | **2,979** | **638** | **17,763** |

## Rollback

To rollback this migration:

```bash
poetry run nes migration rollback 007-source-projects
```

This will remove all project entities, auto-created organizations, and relationships created by this migration.

## Notes

- The DFMIS API requires session cookies (handled automatically)
- Raw API responses are cached to `all_projects.json` for faster re-runs
- Location matching uses aliases for common misspellings
- Organizations are deduplicated by name before creation
- Projects without titles are skipped
