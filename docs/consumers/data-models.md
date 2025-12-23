# Data Models

This document describes the data models used in the Nepal Entity Service. All models are defined using Pydantic for validation and serialization.

## Entity Model

Entities represent persons, organizations, and locations in Nepal's political and administrative landscape.

### Entity Schema

```json
{
  "id": "string (computed)",
  "slug": "string (required, 3-50 chars, kebab-case)",
  "type": "person | organization | location",
  "sub_type": "string (optional, depends on type)",
  "names": [
    {
      "kind": "PRIMARY | ALIAS | ALTERNATE | BIRTH | OFFICIAL",
      "en": {
        "full": "string",
        "given": "string (optional)",
        "middle": "string (optional)",
        "family": "string (optional)",
        "prefix": "string (optional)",
        "suffix": "string (optional)"
      },
      "ne": {
        "full": "string",
        "given": "string (optional)",
        "middle": "string (optional)",
        "family": "string (optional)",
        "prefix": "string (optional)",
        "suffix": "string (optional)"
      }
    }
  ],
  "version_summary": {
    "version": "integer",
    "created_at": "datetime",
    "created_by": "string"
  },
  "identifiers": [
    {
      "scheme": "string (e.g., wikipedia, wikidata, twitter)",
      "value": "string",
      "url": "string (optional)"
    }
  ],
  "attributes": {
    "key": "value (flexible key-value pairs)"
  },
  "contacts": [
    {
      "type": "EMAIL | PHONE | URL | ADDRESS",
      "value": "string"
    }
  ],
  "descriptions": {
    "en": {
      "value": "string",
      "provenance": "human | llm | scraped"
    },
    "ne": {
      "value": "string",
      "provenance": "human | llm | scraped"
    }
  }
}
```

### Entity Types and Subtypes

#### Person

Represents individual persons (politicians, public officials, etc.).

**Type**: `person`

**Subtypes**: None (persons don't have subtypes)

**Common Attributes**:
- `party`: Political party affiliation
- `position`: Current position or role
- `occupation`: Primary occupation
- `birth_date`: Date of birth
- `birth_place`: Place of birth

**Example**:

```json
{
  "id": "entity:person/ram-chandra-poudel",
  "slug": "ram-chandra-poudel",
  "type": "person",
  "names": [
    {
      "kind": "PRIMARY",
      "en": {
        "full": "Ram Chandra Poudel",
        "given": "Ram Chandra",
        "family": "Poudel"
      },
      "ne": {
        "full": "राम चन्द्र पौडेल"
      }
    }
  ],
  "attributes": {
    "party": "nepali-congress",
    "position": "president",
    "birth_date": "1944-10-06"
  }
}
```

#### Organization

Represents organizations, institutions, and groups.

**Type**: `organization`

**Subtypes**:
- `political_party`: Political parties
- `government_body`: Government ministries, departments, agencies
- `ngo`: Non-governmental organizations
- `private_company`: Private sector companies
- `international_org`: International organizations

**Common Attributes**:
- `founded_date`: Date of establishment
- `headquarters`: Location of headquarters
- `website`: Official website URL
- `registration_number`: Official registration number

**Example**:

```json
{
  "id": "entity:organization/political_party/nepali-congress",
  "slug": "nepali-congress",
  "type": "organization",
  "sub_type": "political_party",
  "names": [
    {
      "kind": "PRIMARY",
      "en": {
        "full": "Nepali Congress"
      },
      "ne": {
        "full": "नेपाली कांग्रेस"
      }
    }
  ],
  "attributes": {
    "founded_date": "1947-01-25",
    "ideology": "social-democracy",
    "symbol": "tree"
  }
}
```

#### Location

Represents geographic locations in Nepal's administrative hierarchy.

**Type**: `location`

**Subtypes**:
- `province`: Federal provinces (7 provinces)
- `district`: Districts (77 districts)
- `metropolitan_city`: Metropolitan cities
- `sub_metropolitan_city`: Sub-metropolitan cities
- `municipality`: Municipalities
- `rural_municipality`: Rural municipalities
- `ward`: Electoral wards

**Common Attributes**:
- `code`: Official administrative code
- `population`: Population count
- `area_sq_km`: Area in square kilometers
- `parent_location`: Parent location ID

**Example**:

```json
{
  "id": "entity:location/province/bagmati",
  "slug": "bagmati",
  "type": "location",
  "sub_type": "province",
  "names": [
    {
      "kind": "PRIMARY",
      "en": {
        "full": "Bagmati Province"
      },
      "ne": {
        "full": "बागमती प्रदेश"
      }
    }
  ],
  "attributes": {
    "code": "3",
    "capital": "Hetauda",
    "population": "6101530",
    "area_sq_km": "20300"
  }
}
```

### Name Structure

Names support multilingual variants with structured components:

**Name Kinds**:
- `PRIMARY`: Main name used for the entity
- `ALIAS`: Alternative name or nickname
- `ALTERNATE`: Alternate spelling or transliteration
- `BIRTH`: Birth name (if different from current name)
- `OFFICIAL`: Official legal name

**Name Components**:
- `full`: Complete name (required)
- `first`: First name or given name
- `middle`: Middle name(s)
- `last`: Last name or family name
- `prefix`: Title or prefix (e.g., "Dr.", "Hon.")
- `suffix`: Suffix (e.g., "Jr.", "PhD")

### Identifiers

External identifiers link entities to other systems:

**Common Schemes**:
- `wikipedia`: Wikipedia page name
- `wikidata`: Wikidata Q-number
- `twitter`: Twitter handle
- `facebook`: Facebook page ID
- `official_website`: Official website URL
- `election_commission`: Election Commission ID

### Attributes

Flexible key-value pairs for entity-specific data. Common patterns:

**Person Attributes**:
- `party`, `position`, `occupation`
- `birth_date`, `birth_place`
- `education`, `alma_mater`

**Organization Attributes**:
- `founded_date`, `headquarters`
- `registration_number`, `website`
- `ideology`, `symbol`

**Location Attributes**:
- `code`, `population`, `area_sq_km`
- `parent_location`, `capital`

## Relationship Model

Relationships represent connections between entities.

### Relationship Schema

```json
{
  "id": "string (computed)",
  "source_entity_id": "string (required)",
  "target_entity_id": "string (required)",
  "type": "string (required)",
  "start_date": "date (optional)",
  "end_date": "date (optional)",
  "attributes": {
    "key": "value"
  },
  "version_summary": {
    "version": "integer",
    "created_at": "datetime",
    "created_by": "string"
  },
  "attributions": ["string"]
}
```

### Relationship Types

**Common Relationship Types**:

- `MEMBER_OF`: Person is a member of an organization
- `AFFILIATED_WITH`: Entity is affiliated with another entity
- `EMPLOYED_BY`: Person is employed by an organization
- `REPRESENTS`: Person represents a location (constituency)
- `LOCATED_IN`: Entity is located in a location
- `PART_OF`: Location is part of another location
- `LEADS`: Person leads an organization
- `FOUNDED`: Person founded an organization

### Temporal Relationships

Relationships can have start and end dates:

```json
{
  "source_entity_id": "entity:person/ram-chandra-poudel",
  "target_entity_id": "entity:organization/political_party/nepali-congress",
  "type": "MEMBER_OF",
  "start_date": "2000-01-01",
  "end_date": null,
  "attributes": {
    "role": "president",
    "status": "active"
  }
}
```

**Temporal Queries**:
- `currently_active=true`: Relationships without end date
- Date range filtering: Find relationships active during a period

### Relationship Attributes

Relationship-specific metadata:

**MEMBER_OF Attributes**:
- `role`: Role within organization
- `status`: active, inactive, suspended
- `membership_type`: full, associate, honorary

**REPRESENTS Attributes**:
- `constituency`: Electoral constituency
- `term_start`: Start of term
- `term_end`: End of term
- `election_year`: Year of election

**EMPLOYED_BY Attributes**:
- `position`: Job title
- `department`: Department or division
- `employment_type`: full-time, part-time, contract

## Version Model

Versions provide complete audit trails for entities and relationships.

### Version Schema

```json
{
  "entity_or_relationship_id": "string (required)",
  "version_number": "integer (required)",
  "author": "string (required)",
  "created_at": "datetime (required)",
  "change_description": "string (optional)",
  "snapshot": {
    "...": "complete entity or relationship state"
  },
  "attribution": {
    "source": "string",
    "confidence": "number",
    "method": "string"
  }
}
```

### Version History

Every change creates a new version:

1. **Version 1**: Initial creation
2. **Version 2**: First update
3. **Version 3**: Second update
4. ...and so on

**Version Metadata**:
- `version_number`: Sequential version number
- `author`: Who made the change (author ID)
- `created_at`: When the change was made
- `change_description`: Why the change was made
- `snapshot`: Complete state at that version

### Author Model

Authors represent who made changes:

**Author Types**:
- `author:system:*`: System-generated changes (importers, scrapers)
- `author:human:*`: Human data maintainers
- `author:api:*`: API-initiated changes (future)

**Example Authors**:
- `author:system:csv-importer`: CSV import script
- `author:system:wikipedia-scraper`: Wikipedia scraper
- `author:human:data-maintainer`: Human data maintainer
- `author:human:researcher`: Research team member

## Validation Rules

### Entity Validation

- **Slug**: 3-50 characters, kebab-case, lowercase
- **Names**: At least one name with `kind="PRIMARY"`
- **Type**: Must be `person`, `organization`, or `location`
- **Subtype**: Must be valid for the entity type

### Relationship Validation

- **Entity IDs**: Both source and target must exist
- **Type**: Must be a valid relationship type
- **Dates**: `end_date` must be after `start_date`
- **Circular References**: Prevented for hierarchical relationships

### Name Validation

- **Full Name**: Required for all names
- **Language**: At least one language (en or ne) required
- **Components**: If provided, must be consistent with full name

## Data Quality

### Provenance Tracking

All data includes provenance information:

- **Source**: Where the data came from
- **Method**: How it was obtained (human, llm, scraped)
- **Confidence**: Confidence level (0.0-1.0)
- **Timestamp**: When it was added

### Change Descriptions

All changes should include descriptions:

```json
{
  "change_description": "Updated party affiliation based on official announcement"
}
```

## Examples

### Complete Person Entity

```json
{
  "id": "entity:person/sher-bahadur-deuba",
  "slug": "sher-bahadur-deuba",
  "type": "person",
  "names": [
    {
      "kind": "PRIMARY",
      "en": {
        "full": "Sher Bahadur Deuba",
        "given": "Sher Bahadur",
        "family": "Deuba"
      },
      "ne": {
        "full": "शेर बहादुर देउबा"
      }
    }
  ],
  "version_summary": {
    "version": 3,
    "created_at": "2024-01-20T10:30:00Z",
    "created_by": "author:human:data-maintainer"
  },
  "identifiers": [
    {
      "scheme": "wikipedia",
      "value": "Sher_Bahadur_Deuba",
      "url": "https://en.wikipedia.org/wiki/Sher_Bahadur_Deuba"
    },
    {
      "scheme": "wikidata",
      "value": "Q57363"
    }
  ],
  "attributes": {
    "party": "nepali-congress",
    "position": "prime-minister",
    "birth_date": "1946-06-13",
    "birth_place": "Dadeldhura"
  },
  "contacts": [],
  "descriptions": {
    "en": {
      "value": "Nepali politician who has served as Prime Minister of Nepal five times",
      "provenance": "human"
    },
    "ne": {
      "value": "नेपाली राजनीतिज्ञ जसले पाँच पटक नेपालको प्रधानमन्त्रीको रूपमा सेवा गरेका छन्",
      "provenance": "human"
    }
  }
}
```

### Complete Relationship

```json
{
  "id": "relationship:abc123def456",
  "source_entity_id": "entity:person/sher-bahadur-deuba",
  "target_entity_id": "entity:organization/political_party/nepali-congress",
  "type": "MEMBER_OF",
  "start_date": "1990-01-01",
  "end_date": null,
  "attributes": {
    "role": "president",
    "status": "active",
    "membership_type": "full"
  },
  "version_summary": {
    "version": 2,
    "created_at": "2024-01-20T10:30:00Z",
    "created_by": "author:human:data-maintainer"
  },
  "attributions": [
    "https://nepalikhabar.com/article/...",
    "Official party records"
  ]
}
```

## Project Model

Projects represent development projects in Nepal, aggregating data from multiple sources into a unified DFMIS-compatible structure.

### Design Philosophy

The Project model is designed to:

1. **Align with DFMIS** - Nepal's Ministry of Finance Development Finance Information Management System is the target schema
2. **Support multiple donors** - A single project can have financing from World Bank, ADB, JICA, and bilateral donors
3. **Preserve source data** - Original donor payloads are kept in `donor_extensions` for traceability
4. **Use relationships for linking** - Agencies and locations are linked via entity relationships, not embedded

### Project Schema

```json
{
  "id": "entity:project/development_project/dfmis-12345",
  "slug": "dfmis-12345",
  "type": "project",
  "sub_type": "development_project",
  "stage": "ongoing",
  "implementing_agency": "Department of Roads",
  "executing_agency": "Ministry of Physical Infrastructure",
  "financing": [
    {
      "donor": "World Bank",
      "donor_id": "entity:organization/international_org/world-bank",
      "amount": 150000000,
      "currency": "USD",
      "assistance_type": "loan",
      "budget_type": "on_budget",
      "terms": {
        "interest_rate": 1.25,
        "repayment_period_years": 30,
        "grace_period_years": 5,
        "tying_status": "untied"
      }
    }
  ],
  "total_commitment": 150000000,
  "total_disbursement": 45000000,
  "dates": [
    {"date": "2020-03-15", "type": "APPROVAL", "source": "WB"},
    {"date": "2020-09-01", "type": "EFFECTIVENESS", "source": "WB"},
    {"date": "2025-12-31", "type": "CLOSING", "source": "WB"}
  ],
  "sectors": [
    {
      "normalized_sector": "Transport",
      "donor_sector": "Roads and highways",
      "percentage": 100
    }
  ],
  "donor_extensions": [
    {
      "donor": "WB",
      "donor_project_id": "P123456",
      "raw_payload": {"...": "original WB API response"}
    }
  ],
  "project_url": "https://projects.worldbank.org/en/projects-operations/project-detail/P123456"
}
```

### Project Lifecycle Stages

The `stage` field tracks where a project is in its lifecycle:

| Stage | Description |
|-------|-------------|
| `pipeline` | Under consideration, not yet approved |
| `planning` | Approved but not yet started |
| `approved` | Formally approved, awaiting effectiveness |
| `ongoing` | Currently being implemented |
| `completed` | Successfully finished |
| `suspended` | Temporarily halted |
| `terminated` | Ended before completion |
| `cancelled` | Cancelled before starting |
| `unknown` | Status not available |

### Financing Model

The `financing` array captures all financial commitments and disbursements. Each entry represents a single commitment from a donor.

#### Assistance Types

| Type | Description |
|------|-------------|
| `grant` | Non-repayable funding |
| `loan` | Repayable funding with terms |
| `technical_assistance` | Expert support, training, capacity building |
| `in_kind` | Non-monetary contributions (equipment, materials) |
| `mixed` | Combination of grant and loan |
| `other` | Other assistance types |

#### Budget Types

| Type | Description |
|------|-------------|
| `on_budget` | Recorded in Nepal's national budget |
| `off_budget` | Not recorded in national budget (direct implementation) |

#### Financing Terms (for loans)

```json
{
  "interest_rate": 1.25,
  "repayment_period_years": 30,
  "grace_period_years": 5,
  "tying_status": "untied"
}
```

**Tying Status Values**:
- `tied` - Must be spent in donor country
- `untied` - Can be spent anywhere
- `partially_tied` - Some restrictions apply
- `general_untied` - Untied with general conditions

### Date Events

Projects have multiple milestone dates from different sources:

```json
{
  "dates": [
    {"date": "2020-03-15", "type": "APPROVAL", "source": "WB"},
    {"date": "2020-06-01", "type": "AGREEMENT", "source": "DFMIS"},
    {"date": "2020-09-01", "type": "EFFECTIVENESS", "source": "WB"},
    {"date": "2020-10-15", "type": "START", "source": "DFMIS"},
    {"date": "2025-12-31", "type": "CLOSING", "source": "WB"},
    {"date": "2026-06-30", "type": "COMPLETION", "source": "DFMIS"}
  ]
}
```

**Common Date Types**:
- `APPROVAL` - Board/government approval date
- `AGREEMENT` - Loan/grant agreement signed
- `EFFECTIVENESS` - Agreement becomes effective
- `START` - Implementation begins
- `COMPLETION` - Physical completion
- `CLOSING` - Financial closing (final disbursement)

### Sector Classification

Projects are classified by sector, preserving both normalized (MoF) and original donor classifications:

```json
{
  "sectors": [
    {
      "normalized_sector": "Transport",
      "donor_sector": "Roads and highways",
      "donor_subsector": "National highways",
      "donor": "WB",
      "percentage": 70
    },
    {
      "normalized_sector": "Urban Development",
      "donor_sector": "Urban transport",
      "donor": "WB",
      "percentage": 30
    }
  ]
}
```

### Cross-Cutting Tags

Policy markers and thematic tags:

```json
{
  "tags": [
    {"category": "CLIMATE", "normalized_tag": "climate_adaptation", "donor_tag": "Climate co-benefits"},
    {"category": "GENDER", "normalized_tag": "gender_mainstreaming", "donor_tag": "GEN-2"},
    {"category": "SDG", "normalized_tag": "sdg_9", "donor_tag": "SDG 9: Industry, Innovation"}
  ]
}
```

**Tag Categories**:
- `GENDER` - Gender equality markers
- `CLIMATE` - Climate change markers
- `DISABILITY` - Disability inclusion
- `SDG` - Sustainable Development Goals
- `GOVERNANCE` - Governance themes
- `THEME` - Other thematic areas

### Donor Extensions

Original donor data is preserved for traceability and future re-processing:

```json
{
  "donor_extensions": [
    {
      "donor": "WB",
      "donor_project_id": "P123456",
      "raw_payload": {
        "id": "P123456",
        "project_name": "Nepal: Strategic Roads Connectivity",
        "boardapprovaldate": "2020-03-15",
        "totalamt": 150000000,
        "...": "complete original API response"
      }
    },
    {
      "donor": "ADB",
      "donor_project_id": "NEP-12345",
      "raw_payload": {
        "iati_identifier": "XM-DAC-46004-NEP-12345",
        "...": "complete IATI activity"
      }
    }
  ]
}
```

### Project Relationships

Projects link to other entities via relationships:

| Relationship Type | Target Entity | Description |
|-------------------|---------------|-------------|
| `FUNDED_BY` | Organization | Donor providing financing |
| `IMPLEMENTED_BY` | Organization | Agency implementing the project |
| `EXECUTED_BY` | Organization | Agency executing the project |
| `OVERSEEN_BY` | Organization | Government ministry with oversight |
| `LOCATED_IN` | Location | Geographic location(s) of project |

**Example Relationships**:

```json
[
  {
    "source_entity_id": "entity:project/development_project/dfmis-12345",
    "target_entity_id": "entity:organization/international_org/world-bank",
    "type": "FUNDED_BY"
  },
  {
    "source_entity_id": "entity:project/development_project/dfmis-12345",
    "target_entity_id": "entity:organization/government_body/department-of-roads",
    "type": "IMPLEMENTED_BY"
  },
  {
    "source_entity_id": "entity:project/development_project/dfmis-12345",
    "target_entity_id": "entity:location/district/kathmandu",
    "type": "LOCATED_IN"
  }
]
```

### Data Source Mappings

The Project model unifies data from multiple sources:

| Field | DFMIS | World Bank | ADB (IATI) | JICA |
|-------|-------|------------|------------|------|
| `stage` | `project_status` | `status` | `activity_status` | Derived |
| `financing[].amount` | `commitment[].amount` | `totalamt` | `budget[].value` | `Amount of approval` |
| `financing[].donor` | `commitment[].organization` | "World Bank" | `participating_org` | "JICA" |
| `dates[]` | Multiple date fields | `boardapprovaldate`, `closingdate` | `activity_date[]` | `Date of approval` |
| `sectors[]` | `sector__name` | `major_sectors[]` | `sector[]` | `sector`, `subsector` |

### Complete Project Example

```json
{
  "id": "entity:project/development_project/dfmis-12345",
  "slug": "dfmis-12345",
  "type": "project",
  "sub_type": "development_project",
  "names": [
    {
      "kind": "PRIMARY",
      "en": {"full": "Nepal: Strategic Roads Connectivity and Trade Improvement Project"},
      "ne": {"full": "नेपाल: रणनीतिक सडक सम्पर्क र व्यापार सुधार परियोजना"}
    }
  ],
  "description": {
    "en": {
      "value": "The project aims to improve road connectivity and reduce travel time along strategic corridors in Nepal's Terai region.",
      "provenance": "imported"
    }
  },
  "stage": "ongoing",
  "implementing_agency": "Department of Roads",
  "executing_agency": "Ministry of Physical Infrastructure and Transport",
  "financing": [
    {
      "donor": "World Bank",
      "donor_id": "entity:organization/international_org/world-bank",
      "amount": 150000000,
      "currency": "USD",
      "assistance_type": "loan",
      "financing_instrument": "Investment Project Financing",
      "budget_type": "on_budget",
      "terms": {
        "interest_rate": 1.25,
        "repayment_period_years": 30,
        "grace_period_years": 5,
        "tying_status": "untied"
      },
      "transaction_date": "2020-03-15",
      "transaction_type": "commitment",
      "is_actual": true,
      "source": "WB"
    },
    {
      "donor": "Government of Nepal",
      "amount": 30000000,
      "currency": "USD",
      "assistance_type": "grant",
      "budget_type": "on_budget",
      "transaction_type": "commitment",
      "source": "DFMIS"
    }
  ],
  "total_commitment": 180000000,
  "total_disbursement": 67500000,
  "dates": [
    {"date": "2020-03-15", "type": "APPROVAL", "source": "WB"},
    {"date": "2020-06-01", "type": "AGREEMENT", "source": "DFMIS"},
    {"date": "2020-09-01", "type": "EFFECTIVENESS", "source": "WB"},
    {"date": "2025-12-31", "type": "CLOSING", "source": "WB"}
  ],
  "sectors": [
    {
      "normalized_sector": "Transport",
      "donor_sector": "Roads and highways",
      "donor_subsector": "National highways",
      "donor": "WB",
      "percentage": 100
    }
  ],
  "tags": [
    {"category": "CLIMATE", "normalized_tag": "climate_adaptation"},
    {"category": "GENDER", "normalized_tag": "gender_mainstreaming"}
  ],
  "donor_extensions": [
    {
      "donor": "WB",
      "donor_project_id": "P123456",
      "raw_payload": {
        "id": "P123456",
        "project_name": "Nepal: Strategic Roads Connectivity",
        "countryshortname": "Nepal",
        "regionname": "South Asia",
        "boardapprovaldate": "2020-03-15",
        "closingdate": "2025-12-31",
        "totalamt": 150000000,
        "grantamt": 0,
        "status": "Active"
      }
    }
  ],
  "project_url": "https://projects.worldbank.org/en/projects-operations/project-detail/P123456",
  "identifiers": [
    {
      "scheme": "other",
      "value": "12345",
      "url": "https://dfims.mof.gov.np/project/12345",
      "name": {"en": {"value": "MoF DFMIS Project ID"}}
    }
  ],
  "attributions": [
    {
      "title": {"en": {"value": "MoF DFMIS"}},
      "details": {"en": {"value": "Imported from Nepal Ministry of Finance DFMIS"}}
    }
  ]
}
```

## Next Steps

- [API Reference](/docs) - Interactive OpenAPI documentation
- [Examples](/consumers/examples) - See real-world usage examples
- [Getting Started](/consumers/getting-started) - Start using the API
