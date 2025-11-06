"""Unit tests for EntityDatabase abstract class and implementations."""

import shutil
import tempfile
from abc import ABC
from datetime import date, datetime

import pytest

from nes.core.models.base import Name, NameKind, NameParts
from nes.core.models.organization import Organization
from nes.core.models.person import Person
from nes.core.models.relationship import Relationship
from nes.core.models.version import Actor, Version, VersionSummary, VersionType
from nes.database import get_database
from nes.database.entity_database import EntityDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db = get_database(temp_dir)
    yield db
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_actor():
    """Create a sample actor for testing."""
    return Actor(slug="miraj-dhungana", name="Miraj Dhungana")


@pytest.fixture
def sample_version(sample_actor):
    """Create a sample version for testing."""
    return Version(
        entity_or_relationship_id="entity:person/harka-sampang",
        type="ENTITY",
        version_number=1,
        actor=sample_actor,
        change_description="Test version",
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_version_summary(sample_actor):
    """Create a sample version summary for testing."""
    return VersionSummary(
        entity_or_relationship_id="entity:person/harka-sampang",
        type=VersionType.ENTITY,
        version_number=1,
        actor=sample_actor,
        change_description="Test version",
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
        slug="nepal-communist-party",
        type="organization",
        names=[Name(kind=NameKind.PRIMARY, en=NameParts(full="Nepal Communist Party"))],
        version_summary=sample_version_summary,
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_relationship(sample_version_summary):
    """Create a sample relationship for testing."""
    return Relationship(
        source_entity_id="entity:person/harka-sampang",
        target_entity_id="entity:organization/nepal-communist-party",
        type="MEMBER_OF",
        start_date=date(2020, 1, 1),
        version_summary=sample_version_summary,
        created_at=datetime.now(),
    )


def test_entity_database_is_abstract():
    """Test that EntityDatabase is an abstract class."""
    assert issubclass(EntityDatabase, ABC)

    with pytest.raises(TypeError):
        EntityDatabase()


@pytest.mark.asyncio
async def test_complete_crud_workflow(
    temp_db,
    sample_person,
    sample_organization,
    sample_relationship,
    sample_version,
    sample_actor,
):
    """Test complete CRUD workflow for all entity types."""

    # Test Actor CRUD
    actor_result = await temp_db.put_actor(sample_actor)
    assert actor_result == sample_actor

    retrieved_actor = await temp_db.get_actor(sample_actor.id)
    assert retrieved_actor.slug == sample_actor.slug

    # Test Version CRUD
    version_result = await temp_db.put_version(sample_version)
    assert version_result == sample_version

    retrieved_version = await temp_db.get_version(sample_version.id)
    assert retrieved_version.version_number == sample_version.version_number

    # Test Entity CRUD
    person_result = await temp_db.put_entity(sample_person)
    assert person_result == sample_person

    org_result = await temp_db.put_entity(sample_organization)
    assert org_result == sample_organization

    retrieved_person = await temp_db.get_entity(sample_person.id)
    assert retrieved_person.slug == sample_person.slug

    # Test Relationship CRUD
    rel_result = await temp_db.put_relationship(sample_relationship)
    assert rel_result == sample_relationship

    retrieved_rel = await temp_db.get_relationship(sample_relationship.id)
    assert retrieved_rel.type == sample_relationship.type

    # Test List operations
    entities = await temp_db.list_entities()
    assert len(entities) == 2

    relationships = await temp_db.list_relationships()
    assert len(relationships) == 1

    versions = await temp_db.list_versions()
    assert len(versions) == 1

    actors = await temp_db.list_actors()
    assert len(actors) == 1

    # Test Delete operations
    assert await temp_db.delete_relationship(sample_relationship.id) is True
    assert await temp_db.delete_entity(sample_person.id) is True
    assert await temp_db.delete_entity(sample_organization.id) is True
    assert await temp_db.delete_version(sample_version.id) is True
    assert await temp_db.delete_actor(sample_actor.id) is True

    # Verify deletions
    assert await temp_db.get_relationship(sample_relationship.id) is None
    assert await temp_db.get_entity(sample_person.id) is None
    assert await temp_db.get_entity(sample_organization.id) is None
    assert await temp_db.get_version(sample_version.id) is None
    assert await temp_db.get_actor(sample_actor.id) is None


@pytest.mark.asyncio
async def test_pagination_consistency(temp_db, sample_version):
    """Test that pagination works consistently across all list operations."""

    # Create test data
    actors = [Actor(slug=f"actor-{i}", name=f"Actor {i}") for i in range(10)]
    for actor in actors:
        await temp_db.put_actor(actor)

    versions = []
    for i in range(10):
        version = Version(
            entity_or_relationship_id=f"entity:person/person-{i}",
            type="ENTITY",
            version_number=i + 1,
            actor=actors[0],
            change_description=f"Version {i}",
            created_at=datetime.now(),
        )
        versions.append(version)
        await temp_db.put_version(version)

    entities = []
    for i in range(10):
        version_summary = VersionSummary(
            entity_or_relationship_id=f"entity:person/person-{i}",
            type="ENTITY",
            version_number=1,
            actor=actors[0],
            change_description=f"Person {i} version",
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

    relationships = []
    for i in range(10):
        rel_version_summary = VersionSummary(
            entity_or_relationship_id=f"relationship:person-{i}:org-{i}",
            type="RELATIONSHIP",
            version_number=1,
            actor=actors[0],
            change_description=f"Relationship {i} version",
            created_at=datetime.now(),
        )
        relationship = Relationship(
            source_entity_id=f"entity:person/person-{i}",
            target_entity_id=f"entity:organization/org-{i}",
            type="MEMBER_OF",
            version_summary=rel_version_summary,
            created_at=datetime.now(),
        )
        relationships.append(relationship)
        await temp_db.put_relationship(relationship)

    # Test pagination
    page_size = 3

    # Test actors pagination
    page1_actors = await temp_db.list_actors(limit=page_size, offset=0)
    page2_actors = await temp_db.list_actors(limit=page_size, offset=page_size)
    assert len(page1_actors) == page_size
    assert len(page2_actors) == page_size

    # Test versions pagination
    page1_versions = await temp_db.list_versions(limit=page_size, offset=0)
    page2_versions = await temp_db.list_versions(limit=page_size, offset=page_size)
    assert len(page1_versions) == page_size
    assert len(page2_versions) == page_size

    # Test entities pagination
    page1_entities = await temp_db.list_entities(limit=page_size, offset=0)
    page2_entities = await temp_db.list_entities(limit=page_size, offset=page_size)
    assert len(page1_entities) == page_size
    assert len(page2_entities) == page_size

    # Test relationships pagination
    page1_rels = await temp_db.list_relationships(limit=page_size, offset=0)
    page2_rels = await temp_db.list_relationships(limit=page_size, offset=page_size)
    assert len(page1_rels) == page_size
    assert len(page2_rels) == page_size
