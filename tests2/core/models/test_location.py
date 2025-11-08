"""Tests for Location model in nes2."""

import pytest
from datetime import datetime, UTC
from pydantic import ValidationError

from nes2.core.models.base import Name, NameKind
from nes2.core.models.entity import EntitySubType
from nes2.core.models.location import Location, LocationType
from nes2.core.models.version import Author, VersionSummary, VersionType


def test_location_basic_creation():
    """Test creating a basic Location entity."""
    
    location = Location(
        slug="test-location",
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Location"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/test-location",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert location.type == "location"
    assert location.slug == "test-location"
    assert location.id == "entity:location/test-location"


def test_location_province():
    """Test creating a Province location."""
    
    province = Location(
        slug="bagmati-province",
        sub_type=EntitySubType.PROVINCE,
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Bagmati Province"},
                ne={"full": "बागमती प्रदेश"}
            )
        ],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/province/bagmati-province",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert province.sub_type == EntitySubType.PROVINCE
    assert province.location_type == LocationType.PROVINCE
    assert province.administrative_level == 1
    assert province.id == "entity:location/province/bagmati-province"


def test_location_district():
    """Test creating a District location."""
    
    district = Location(
        slug="kathmandu-district",
        sub_type=EntitySubType.DISTRICT,
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Kathmandu District"},
                ne={"full": "काठमाडौं जिल्ला"}
            )
        ],
        parent="entity:location/province/bagmati-province",
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/district/kathmandu-district",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert district.sub_type == EntitySubType.DISTRICT
    assert district.location_type == LocationType.DISTRICT
    assert district.administrative_level == 2
    assert district.parent == "entity:location/province/bagmati-province"


def test_location_metropolitan_city():
    """Test creating a Metropolitan City location."""
    
    metro = Location(
        slug="kathmandu-metropolitan-city",
        sub_type=EntitySubType.METROPOLITAN_CITY,
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Kathmandu Metropolitan City"},
                ne={"full": "काठमाडौं महानगरपालिका"}
            )
        ],
        parent="entity:location/district/kathmandu-district",
        area=49.45,
        lat=27.7172,
        lng=85.3240,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/metropolitan_city/kathmandu-metropolitan-city",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert metro.sub_type == EntitySubType.METROPOLITAN_CITY
    assert metro.location_type == LocationType.METROPOLITAN_CITY
    assert metro.administrative_level == 3
    assert metro.area == 49.45
    assert metro.lat == 27.7172
    assert metro.lng == 85.3240


def test_location_municipality():
    """Test creating a Municipality location."""
    
    municipality = Location(
        slug="pokhara-metropolitan-city",
        sub_type=EntitySubType.METROPOLITAN_CITY,
        names=[
            Name(
                kind=NameKind.PRIMARY,
                en={"full": "Pokhara Metropolitan City"},
                ne={"full": "पोखरा महानगरपालिका"}
            )
        ],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/metropolitan_city/pokhara-metropolitan-city",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert municipality.location_type == LocationType.METROPOLITAN_CITY
    assert municipality.administrative_level == 3


def test_location_ward():
    """Test creating a Ward location."""
    
    ward = Location(
        slug="kathmandu-ward-1",
        sub_type=EntitySubType.WARD,
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Ward 1"})],
        parent="entity:location/metropolitan_city/kathmandu-metropolitan-city",
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/ward/kathmandu-ward-1",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert ward.sub_type == EntitySubType.WARD
    assert ward.location_type == LocationType.WARD
    assert ward.administrative_level == 4


def test_location_constituency():
    """Test creating a Constituency location."""
    
    constituency = Location(
        slug="kathmandu-1",
        sub_type=EntitySubType.CONSTITUENCY,
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Kathmandu Constituency 1"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/constituency/kathmandu-1",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert constituency.sub_type == EntitySubType.CONSTITUENCY
    assert constituency.location_type == LocationType.CONSTITUENCY
    assert constituency.administrative_level is None  # Electoral boundary, not administrative


def test_location_with_coordinates():
    """Test Location with geographic coordinates."""
    
    location = Location(
        slug="test-location",
        sub_type=EntitySubType.MUNICIPALITY,
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Test Location"})],
        lat=27.7172,
        lng=85.3240,
        area=100.5,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/municipality/test-location",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert location.lat == 27.7172
    assert location.lng == 85.3240
    assert location.area == 100.5


def test_location_hierarchy():
    """Test location parent-child hierarchy."""
    
    # Province (level 1)
    province = Location(
        slug="bagmati-province",
        sub_type=EntitySubType.PROVINCE,
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Bagmati Province"})],
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/province/bagmati-province",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    # District (level 2) - child of province
    district = Location(
        slug="kathmandu-district",
        sub_type=EntitySubType.DISTRICT,
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Kathmandu District"})],
        parent=province.id,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/district/kathmandu-district",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    # Municipality (level 3) - child of district
    municipality = Location(
        slug="kathmandu-metro",
        sub_type=EntitySubType.METROPOLITAN_CITY,
        names=[Name(kind=NameKind.PRIMARY, en={"full": "Kathmandu Metropolitan City"})],
        parent=district.id,
        version_summary=VersionSummary(
            entity_or_relationship_id="entity:location/metropolitan_city/kathmandu-metro",
            type=VersionType.ENTITY,
            version_number=1,
            author=Author(slug="system"),
            change_description="Initial",
            created_at=datetime.now(UTC)
        ),
        created_at=datetime.now(UTC)
    )
    
    assert province.administrative_level == 1
    assert district.administrative_level == 2
    assert municipality.administrative_level == 3
    assert district.parent == province.id
    assert municipality.parent == district.id
