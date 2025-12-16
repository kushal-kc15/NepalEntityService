"""Project-specific models for nes.

This module is the single source of truth for development projects in Nepal.
It is designed to map data from multiple sources into a DFMIS-compatible structure:
- MoF DFMIS (target schema - Nepal's official aid management system)
- NPC Project Bank (spatial-first, minimal)
- World Bank (narrative + sectors)
- ADB (IATI standard, event-based)
- JICA (loan mechanics)

Design principles:
1. DFMIS as target schema - field names and structures align with MoF system
2. Multi-donor support - financing[] allows multiple commitments per project
3. Source preservation - donor_extensions[] keeps original data for traceability
4. Relationship-based linking - agencies and locations via entity relationships
"""

from datetime import date
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from .entity import Entity, EntitySubType

# =============================================================================
# ENUMS
# =============================================================================


class ProjectStage(str, Enum):
    """Project lifecycle stage - aligned with DFMIS project_status."""

    PIPELINE = "pipeline"
    PLANNING = "planning"
    APPROVED = "approved"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class AssistanceType(str, Enum):
    """Type of development assistance - from DFMIS commitment.assistance_type."""

    GRANT = "grant"
    LOAN = "loan"
    TECHNICAL_ASSISTANCE = "technical_assistance"
    IN_KIND = "in_kind"
    MIXED = "mixed"
    OTHER = "other"
    UNKNOWN = "unknown"


class BudgetType(str, Enum):
    """Budget classification - from DFMIS."""

    ON_BUDGET = "on_budget"
    OFF_BUDGET = "off_budget"
    UNKNOWN = "unknown"


# =============================================================================
# FINANCING MODELS - DFMIS commitment structure as target
# =============================================================================


class FinancingTerms(BaseModel):
    """Loan/grant terms - captures DFMIS commitment details."""

    model_config = ConfigDict(extra="forbid")

    interest_rate: Optional[float] = Field(None, description="Annual interest rate (%)")
    repayment_period_years: Optional[int] = Field(
        None, description="Total repayment period"
    )
    grace_period_years: Optional[int] = Field(
        None, description="Grace period before repayment"
    )
    tying_status: Optional[str] = Field(
        None, description="tied, untied, partially_tied, general_untied"
    )


class FinancingCommitment(BaseModel):
    """Single financing commitment from a donor.

    Aligned with DFMIS commitment[] structure. Each commitment ties a donor
    to their specific contribution with full financing details.

    Source mappings:
    - DFMIS: Direct from commitment[] array
    - WB: Single entry with grantamt/totalamt, donor="World Bank"
    - ADB: Single entry, donor="Asian Development Bank"
    - JICA: May have multiple entries for main/consulting portions
    """

    model_config = ConfigDict(extra="forbid")

    # Donor identification
    donor: str = Field(..., description="Donor organization name")
    donor_id: Optional[str] = Field(
        None, description="Entity ID reference (entity:organization/...)"
    )

    # Amounts
    amount: Optional[float] = Field(None, description="Amount in specified currency")
    currency: Optional[str] = Field(None, description="ISO 4217 currency code")

    # Classification - from DFMIS
    assistance_type: AssistanceType = AssistanceType.UNKNOWN
    financing_instrument: Optional[str] = Field(
        None, description="Project Support, Program-Based Support, Budget Support, etc."
    )
    budget_type: Optional[BudgetType] = None

    # Terms (for loans)
    terms: Optional[FinancingTerms] = None

    # Transaction metadata
    transaction_date: Optional[date] = Field(
        None, description="Date of commitment/disbursement"
    )
    transaction_type: Optional[str] = Field(
        None, description="commitment, disbursement, expenditure"
    )
    is_actual: bool = Field(True, description="False if planned/projected")

    # Source tracking
    source: Optional[str] = Field(None, description="Data source: DFMIS, WB, ADB, JICA")


# =============================================================================
# DATE EVENTS
# =============================================================================


class ProjectDateEvent(BaseModel):
    """Project milestone date.

    Unified model for dates from all sources:
    - DFMIS: Multiple date fields (agreement_date, effectiveness_date, etc.)
    - ADB/IATI: activity_dates[] with type codes
    - WB: boardapprovaldate, closingdate
    - JICA: Date of approval
    """

    model_config = ConfigDict(extra="forbid")

    date: date
    type: str = Field(
        ..., description="APPROVAL, EFFECTIVENESS, START, COMPLETION, CLOSING, etc."
    )
    source: Optional[str] = Field(None, description="DFMIS, WB, ADB, JICA, NPC")


# =============================================================================
# SECTORS AND TAGS
# =============================================================================


class SectorMapping(BaseModel):
    """Sector classification with normalization.

    Each source uses different taxonomies:
    - DFMIS: sector__name (Nepal MoF sectors)
    - WB: major_sectors[] with sector codes
    - ADB: DAC sector codes (IATI vocabulary=1)
    - JICA: sector/subsector text

    We store both normalized (MoF) and original donor values.
    """

    model_config = ConfigDict(extra="forbid")

    normalized_sector: Optional[str] = Field(
        None, description="MoF-normalized sector code or name"
    )
    donor_sector: Optional[str] = Field(
        None, description="Sector as reported by the donor"
    )
    donor_subsector: Optional[str] = None
    donor: Optional[str] = None
    percentage: Optional[float] = Field(
        None, description="Sector allocation percentage (0-100)"
    )


class CrossCuttingTag(BaseModel):
    """Cross-cutting themes and policy markers.

    Maps from:
    - DFMIS: gender, climate, disability_marker fields
    - ADB: policy_markers[] array
    - WB: themev2_level1/level2
    """

    model_config = ConfigDict(extra="forbid")

    category: str = Field(
        ..., description="GENDER, CLIMATE, DISABILITY, SDG, GOVERNANCE, THEME"
    )
    normalized_tag: Optional[str] = None
    donor_tag: Optional[str] = None
    donor: Optional[str] = None


# =============================================================================
# DONOR EXTENSION - Raw payload preservation
# =============================================================================


class DonorExtension(BaseModel):
    """Donor-specific data extension for traceability.

    Preserves original donor payload and identifiers for:
    - Data lineage and audit
    - Future re-processing if schema evolves
    - Donor-specific fields not in unified model
    """

    model_config = ConfigDict(extra="allow")

    donor: str = Field(..., description="WB, ADB, JICA, NPC, DFMIS")
    donor_project_id: Optional[str] = Field(
        None,
        description="WB P-number, ADB IATI identifier, JICA project code, DFMIS id",
    )
    raw_payload: Optional[Dict] = Field(
        None, description="Original donor payload for traceability"
    )


# =============================================================================
# MAIN PROJECT ENTITY
# =============================================================================


class Project(Entity):
    """Development project entity - DFMIS-aligned unified model.

    This entity represents the national view of a project, aggregating data
    from multiple sources (DFMIS, WB, ADB, JICA, NPC) into a single record.

    Location handling:
    - Projects link to location entities via LOCATED_IN relationships
    - No embedded location data (use relationships for multi-location support)

    Agency handling:
    - Primary agencies stored as text fields for quick access
    - Full agency details via FUNDED_BY, IMPLEMENTED_BY, EXECUTED_BY relationships
    - Government oversight via OVERSEEN_BY relationships
    """

    type: Literal["project"] = Field(
        default="project", description="Entity type, always 'project'"
    )
    sub_type: EntitySubType = Field(
        default=EntitySubType.DEVELOPMENT_PROJECT,
        description="Project subtype classification",
    )

    # Lifecycle
    stage: ProjectStage = Field(default=ProjectStage.UNKNOWN)

    # Quick-access agency fields (full details via relationships)
    implementing_agency: Optional[str] = Field(
        None, description="Primary implementing agency name"
    )
    executing_agency: Optional[str] = Field(
        None, description="Primary executing agency name"
    )

    # Financing - DFMIS commitment structure with donor info
    financing: Optional[List[FinancingCommitment]] = Field(
        None, description="Financing commitments/disbursements from donors"
    )

    # Aggregate totals (convenience fields, can be computed from financing[])
    total_commitment: Optional[float] = Field(
        None, description="Total committed amount (usually USD)"
    )
    total_disbursement: Optional[float] = Field(
        None, description="Total disbursed amount (usually USD)"
    )

    # Timeline
    dates: Optional[List[ProjectDateEvent]] = None

    # Classification
    sectors: Optional[List[SectorMapping]] = None
    tags: Optional[List[CrossCuttingTag]] = None

    # Donor extensions for raw payload preservation
    donor_extensions: Optional[List[DonorExtension]] = None

    # Primary project URL (convenience field)
    project_url: Optional[AnyUrl] = None
