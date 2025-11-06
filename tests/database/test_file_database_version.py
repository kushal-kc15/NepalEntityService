"""Unit tests for FileDatabase version operations."""

import shutil
import tempfile
from datetime import datetime

import pytest

from nes.core.models.version import Actor, Version
from nes.database.file_database import FileDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db = FileDatabase(temp_dir)
    yield db
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_actor():
    """Create a sample actor for testing."""
    return Actor(slug="rabindra-mishra", name="Rabindra Mishra")


@pytest.fixture
def sample_version(sample_actor):
    """Create a sample version for testing."""
    return Version(
        entity_or_relationship_id="entity:person/harka-sampang",
        type="ENTITY",
        version_number=1,
        actor=sample_actor,
        change_description="Initial entity creation",
        created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_put_version(temp_db, sample_version):
    """Test putting a version."""
    result = await temp_db.put_version(sample_version)
    assert result == sample_version

    file_path = temp_db._id_to_path(sample_version.id)
    assert file_path.exists()


@pytest.mark.asyncio
async def test_get_version(temp_db, sample_version):
    """Test getting a version."""
    await temp_db.put_version(sample_version)
    result = await temp_db.get_version(sample_version.id)
    assert result.created_at == sample_version.created_at
    assert result.type == sample_version.type
    assert result.version_number == sample_version.version_number


@pytest.mark.asyncio
async def test_get_nonexistent_version(temp_db):
    """Test getting a non-existent version."""
    result = await temp_db.get_version("version:nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_version(temp_db, sample_version):
    """Test deleting a version."""
    await temp_db.put_version(sample_version)
    result = await temp_db.delete_version(sample_version.id)
    assert result is True

    file_path = temp_db._id_to_path(sample_version.id)
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_version(temp_db):
    """Test deleting a non-existent version."""
    result = await temp_db.delete_version("version:nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_list_versions(temp_db, sample_actor):
    """Test listing versions."""
    versions = [
        Version(
            entity_or_relationship_id="entity:person/harka-sampang",
            type="ENTITY",
            version_number=1,
            actor=sample_actor,
            change_description="Initial creation",
            created_at=datetime.now(),
        ),
        Version(
            entity_or_relationship_id="relationship:person/harka-sampang:organization/party:MEMBER_OF",
            type="RELATIONSHIP",
            version_number=1,
            actor=sample_actor,
            change_description="Relationship update",
            created_at=datetime.now(),
        ),
    ]

    for version in versions:
        await temp_db.put_version(version)

    result = await temp_db.list_versions()
    assert len(result) == 2
    assert all(isinstance(version, Version) for version in result)


@pytest.mark.asyncio
async def test_list_versions_with_pagination(temp_db, sample_actor):
    """Test listing versions with pagination."""
    versions = []
    for i in range(5):
        version = Version(
            entity_or_relationship_id=f"entity:person/person-{i}",
            type="ENTITY",
            version_number=i + 1,
            actor=sample_actor,
            change_description=f"Version {i + 1}",
            created_at=datetime.now(),
        )
        versions.append(version)
        await temp_db.put_version(version)

    result = await temp_db.list_versions(limit=2, offset=1)
    assert len(result) == 2
