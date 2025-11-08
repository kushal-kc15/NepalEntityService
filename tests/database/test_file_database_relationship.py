"""Unit tests for FileDatabase relationship operations."""

import shutil
import tempfile
from datetime import date, datetime

import pytest

from nes.core.models.relationship import Relationship
from nes.core.models.version import Actor, VersionSummary
from nes.database.file_database import FileDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db = FileDatabase(temp_dir)
    yield db
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_author():
    """Create a sample author for testing."""
    return Actor(slug="miraj-dhungana", name="Miraj Dhungana")


@pytest.fixture
def sample_version_summary(sample_author):
    """Create a sample version summary for testing."""
    return VersionSummary(
        entity_or_relationship_id="relationship:person/harka-sampang:organization/shram-sanskriti-party:MEMBER_OF",
        type="RELATIONSHIP",
        version_number=1,
        author=sample_author,
        change_description="Initial relationship creation",
        created_at=datetime.now(),
    )


@pytest.fixture
def sample_relationship(sample_version_summary):
    """Create a sample relationship for testing."""
    return Relationship(
        source_entity_id="entity:person/harka-sampang",
        target_entity_id="entity:organization/shram-sanskriti-party",
        type="MEMBER_OF",
        start_date=date(2020, 1, 1),
        version_summary=sample_version_summary,
        created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_put_relationship(temp_db, sample_relationship):
    """Test putting a relationship."""
    result = await temp_db.put_relationship(sample_relationship)
    assert result == sample_relationship

    file_path = temp_db._id_to_path(sample_relationship.id)
    assert file_path.exists()


@pytest.mark.asyncio
async def test_get_relationship(temp_db, sample_relationship):
    """Test getting a relationship."""
    await temp_db.put_relationship(sample_relationship)
    result = await temp_db.get_relationship(sample_relationship.id)
    assert result.source_entity_id == sample_relationship.source_entity_id
    assert result.target_entity_id == sample_relationship.target_entity_id
    assert result.type == sample_relationship.type


@pytest.mark.asyncio
async def test_get_nonexistent_relationship(temp_db):
    """Test getting a non-existent relationship."""
    result = await temp_db.get_relationship("relationship:nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_relationship(temp_db, sample_relationship):
    """Test deleting a relationship."""
    await temp_db.put_relationship(sample_relationship)
    result = await temp_db.delete_relationship(sample_relationship.id)
    assert result is True

    file_path = temp_db._id_to_path(sample_relationship.id)
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_relationship(temp_db):
    """Test deleting a non-existent relationship."""
    result = await temp_db.delete_relationship("relationship:nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_list_relationships(temp_db, sample_author):
    """Test listing relationships."""
    version_summary1 = VersionSummary(
        entity_or_relationship_id="relationship:person/harka-sampang:organization/shram-sanskriti-party:MEMBER_OF",
        type="RELATIONSHIP",
        version_number=1,
        author=sample_author,
        change_description="Relationship 1",
        created_at=datetime.now(),
    )
    version_summary2 = VersionSummary(
        entity_or_relationship_id="relationship:person/rabindra-mishra:organization/rastriya-swatantra-party:AFFILIATED_WITH",
        type="RELATIONSHIP",
        version_number=1,
        author=sample_author,
        change_description="Relationship 2",
        created_at=datetime.now(),
    )
    relationships = [
        Relationship(
            source_entity_id="entity:person/harka-sampang",
            target_entity_id="entity:organization/shram-sanskriti-party",
            type="MEMBER_OF",
            version_summary=version_summary1,
            created_at=datetime.now(),
        ),
        Relationship(
            source_entity_id="entity:person/rabindra-mishra",
            target_entity_id="entity:organization/rastriya-swatantra-party",
            type="AFFILIATED_WITH",
            version_summary=version_summary2,
            created_at=datetime.now(),
        ),
    ]

    for relationship in relationships:
        await temp_db.put_relationship(relationship)

    result = await temp_db.list_relationships()
    assert len(result) == 2
    assert all(isinstance(rel, Relationship) for rel in result)


@pytest.mark.asyncio
async def test_list_relationships_with_pagination(temp_db, sample_author):
    """Test listing relationships with pagination."""
    relationships = []
    for i in range(5):
        version_summary = VersionSummary(
            entity_or_relationship_id=f"relationship:person/person-{i}:organization/org-{i}:MEMBER_OF",
            type="RELATIONSHIP",
            version_number=1,
            author=sample_author,
            change_description=f"Relationship {i}",
            created_at=datetime.now(),
        )
        relationship = Relationship(
            source_entity_id=f"entity:person/person-{i}",
            target_entity_id=f"entity:organization/org-{i}",
            type="MEMBER_OF",
            version_summary=version_summary,
            created_at=datetime.now(),
        )
        relationships.append(relationship)
        await temp_db.put_relationship(relationship)

    result = await temp_db.list_relationships(limit=2, offset=1)
    assert len(result) == 2
