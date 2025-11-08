"""Pytest configuration and fixtures for nes2 tests."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_db_path():
    """Create a temporary database directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_nepali_person():
    """Sample Nepali politician entity data."""
    return {
        "slug": "ram-chandra-poudel",
        "type": "person",
        "sub_type": "politician",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {
                    "full": "Ram Chandra Poudel",
                    "first": "Ram Chandra",
                    "last": "Poudel"
                },
                "ne": {
                    "full": "राम चन्द्र पौडेल",
                    "first": "राम चन्द्र",
                    "last": "पौडेल"
                }
            }
        ],
        "attributes": {
            "party": "nepali-congress",
            "constituency": "Tanahun-1"
        }
    }


@pytest.fixture
def sample_nepali_organization():
    """Sample Nepali political party entity data."""
    return {
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
            "founded": "1947",
            "ideology": "social-democracy"
        }
    }


@pytest.fixture
def sample_nepali_location():
    """Sample Nepali location entity data."""
    return {
        "slug": "kathmandu-metropolitan-city",
        "type": "location",
        "sub_type": "metropolitan_city",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {
                    "full": "Kathmandu Metropolitan City"
                },
                "ne": {
                    "full": "काठमाडौं महानगरपालिका"
                }
            }
        ],
        "attributes": {
            "province": "Bagmati",
            "district": "Kathmandu"
        }
    }


@pytest.fixture
def sample_relationship():
    """Sample relationship between entities."""
    return {
        "source_entity_id": "entity:person/politician/ram-chandra-poudel",
        "target_entity_id": "entity:organization/political_party/nepali-congress",
        "type": "MEMBER_OF",
        "start_date": "2000-01-01",
        "attributes": {
            "position": "President"
        }
    }


@pytest.fixture
def sample_version():
    """Sample version metadata."""
    return {
        "entity_id": "entity:person/politician/ram-chandra-poudel",
        "version": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "created_by": "author:system:csv-importer",
        "change_description": "Initial import"
    }


@pytest.fixture
def authentic_nepali_politicians():
    """List of authentic Nepali politician names for testing."""
    return [
        {
            "slug": "pushpa-kamal-dahal",
            "en": "Pushpa Kamal Dahal",
            "ne": "पुष्पकमल दाहाल",
            "party": "CPN (Maoist Centre)"
        },
        {
            "slug": "khadga-prasad-oli",
            "en": "Khadga Prasad Oli",
            "ne": "खड्ग प्रसाद ओली",
            "party": "CPN-UML"
        },
        {
            "slug": "sher-bahadur-deuba",
            "en": "Sher Bahadur Deuba",
            "ne": "शेरबहादुर देउवा",
            "party": "Nepali Congress"
        },
        {
            "slug": "baburam-bhattarai",
            "en": "Baburam Bhattarai",
            "ne": "बाबुराम भट्टराई",
            "party": "Nepal Samajbadi Party"
        }
    ]


@pytest.fixture
def authentic_nepali_parties():
    """List of authentic Nepali political parties for testing."""
    return [
        {
            "slug": "nepali-congress",
            "en": "Nepali Congress",
            "ne": "नेपाली कांग्रेस"
        },
        {
            "slug": "cpn-uml",
            "en": "Communist Party of Nepal (Unified Marxist-Leninist)",
            "ne": "नेपाल कम्युनिष्ट पार्टी (एकीकृत मार्क्सवादी-लेनिनवादी)"
        },
        {
            "slug": "cpn-maoist-centre",
            "en": "Communist Party of Nepal (Maoist Centre)",
            "ne": "नेपाल कम्युनिष्ट पार्टी (माओवादी केन्द्र)"
        }
    ]


@pytest.fixture
def authentic_nepali_locations():
    """List of authentic Nepali administrative divisions for testing."""
    return [
        {
            "slug": "bagmati-province",
            "type": "province",
            "en": "Bagmati Province",
            "ne": "बागमती प्रदेश"
        },
        {
            "slug": "kathmandu-district",
            "type": "district",
            "en": "Kathmandu District",
            "ne": "काठमाडौं जिल्ला"
        },
        {
            "slug": "pokhara-metropolitan-city",
            "type": "metropolitan_city",
            "en": "Pokhara Metropolitan City",
            "ne": "पोखरा महानगरपालिका"
        }
    ]
