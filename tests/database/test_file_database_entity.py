"""Unit tests for FileDatabase entity operations."""

import shutil
import tempfile
from datetime import datetime

import pytest

from nes.core.models.base import LangText, LangTextValue, Name, NameKind, NameParts
from nes.core.models.entity import Entity
from nes.core.models.organization import Organization
from nes.core.models.person import Education, Person, PersonDetails
from nes.core.models.version import Actor, VersionSummary, VersionType
from nes.database import get_database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db = get_database(temp_dir)
    yield db
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_author():
    """Create a sample author for testing."""
    return Actor(slug="harka-sampang", name="Harka Sampang")


@pytest.fixture
def sample_version_summary(sample_author):
    """Create a sample version summary for testing."""
    return VersionSummary(
        entity_or_relationship_id="entity:person/harka-sampang",
        type=VersionType.ENTITY,
        version_number=1,
        author=sample_author,
        change_description="Initial creation",
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_person(sample_version_summary):
    """Create a sample person entity for testing."""
    return Person(
        slug="harka-sampang",
        names=[Name(kind=NameKind.PRIMARY, en=NameParts(full="Harka Sampang"))],
        version_summary=sample_version_summary,
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_organization(sample_version_summary):
    """Create a sample organization entity for testing."""
    return Organization(
        slug="shram-sanskriti-party",
        type="organization",
        names=[Name(kind=NameKind.PRIMARY, en=NameParts(full="Shram Sanskriti Party"))],
        version_summary=sample_version_summary,
        created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_put_entity(temp_db, sample_person):
    """Test putting an entity."""
    result = await temp_db.put_entity(sample_person)
    assert result == sample_person

    file_path = temp_db._id_to_path(sample_person.id)
    assert file_path.exists()


@pytest.mark.asyncio
async def test_get_entity(temp_db, sample_person):
    """Test getting an entity."""
    await temp_db.put_entity(sample_person)
    result = await temp_db.get_entity(sample_person.id)
    assert result.slug == sample_person.slug
    assert result.type == sample_person.type


@pytest.mark.asyncio
async def test_get_nonexistent_entity(temp_db):
    """Test getting a non-existent entity."""
    result = await temp_db.get_entity("person:nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_entity(temp_db, sample_person):
    """Test deleting an entity."""
    await temp_db.put_entity(sample_person)
    result = await temp_db.delete_entity(sample_person.id)
    assert result is True

    file_path = temp_db._id_to_path(sample_person.id)
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_entity(temp_db):
    """Test deleting a non-existent entity."""
    result = await temp_db.delete_entity("person:nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_list_entities(temp_db, sample_person, sample_organization):
    """Test listing entities."""
    await temp_db.put_entity(sample_person)
    await temp_db.put_entity(sample_organization)

    result = await temp_db.list_entities()
    assert len(result) == 2
    assert all(isinstance(entity, Entity) for entity in result)


@pytest.mark.asyncio
async def test_list_entities_with_pagination(temp_db, sample_author):
    """Test listing entities with pagination."""
    entities = []
    for i in range(5):
        version_summary = VersionSummary(
            entity_or_relationship_id=f"entity:person/person-{i}",
            type="ENTITY",
            version_number=1,
            author=sample_author,
            change_description=f"Person {i} creation",
            created_at=datetime.now(),
        )
        entity = Person(
            slug=f"person-{i}",
            names=[Name(kind=NameKind.PRIMARY, en=NameParts(full=f"Person {i}"))],
            version_summary=version_summary,
            created_at=datetime.now(),
        )
        entities.append(entity)
        await temp_db.put_entity(entity)

    result = await temp_db.list_entities(limit=2, offset=1)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_person_with_education_persistence(temp_db, sample_author):
    """Test that person education info persists after save and retrieval."""
    education = Education(
        institution=LangText(en=LangTextValue(value="Tribhuvan University")),
        degree=LangText(en=LangTextValue(value="Bachelor of Arts")),
        field=LangText(en=LangTextValue(value="Political Science")),
        start_year=2015,
        end_year=2019,
    )

    version_summary = VersionSummary(
        entity_or_relationship_id="entity:person/miraj-dhungana",
        type=VersionType.ENTITY,
        version_number=1,
        author=sample_author,
        change_description="Initial creation",
        created_at=datetime.now(),
    )

    person = Person(
        slug="miraj-dhungana",
        names=[Name(kind=NameKind.PRIMARY, en=NameParts(full="Miraj Dhungana"))],
        version_summary=version_summary,
        created_at=datetime.now(),
        personal_details=PersonDetails(education=[education]),
    )

    await temp_db.put_entity(person)
    retrieved_person: Person = await temp_db.get_entity(person.id)

    assert retrieved_person.personal_details.education is not None
    assert len(retrieved_person.personal_details.education) == 1
    education = retrieved_person.personal_details.education[0]

    assert education.institution.en.value == "Tribhuvan University"
    assert education.degree.en.value == "Bachelor of Arts"
    assert education.field.en.value == "Political Science"
    assert education.start_year == 2015
    assert education.end_year == 2019
