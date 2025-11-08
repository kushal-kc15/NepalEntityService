"""Unit tests for FileDatabase author operations."""

import shutil
import tempfile
from pathlib import Path

import pytest

from nes.core.models.version import Actor
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
    return Actor(slug="harka-sampang", name="Harka Sampang")


@pytest.mark.asyncio
async def test_put_author(temp_db, sample_author):
    """Test putting an author."""
    result = await temp_db.put_author(sample_author)
    assert result == sample_author

    # Verify file exists
    file_path = temp_db._id_to_path(sample_author.id)
    assert file_path.exists()


@pytest.mark.asyncio
async def test_get_author(temp_db, sample_author):
    """Test getting an author."""
    await temp_db.put_author(sample_author)
    result = await temp_db.get_author(sample_author.id)
    assert result.slug == sample_author.slug
    assert result.name == sample_author.name


@pytest.mark.asyncio
async def test_get_nonexistent_actor(temp_db):
    """Test getting a non-existent author."""
    result = await temp_db.get_author("actor:nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_author(temp_db, sample_author):
    """Test deleting an author."""
    await temp_db.put_author(sample_author)
    result = await temp_db.delete_author(sample_author.id)
    assert result is True

    # Verify file is deleted
    file_path = temp_db._id_to_path(sample_author.id)
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_actor(temp_db):
    """Test deleting a non-existent author."""
    result = await temp_db.delete_author("actor:nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_list_actors(temp_db):
    """Test listing actors."""
    authors = [
        Actor(slug="harka-sampang", name="Harka Sampang"),
        Actor(slug="rabindra-mishra", name="Rabindra Mishra"),
    ]

    for author in authors:
        await temp_db.put_author(actor)

    result = await temp_db.list_actors()
    assert len(result) == 2
    assert all(isinstance(author, Actor) for author in result)


@pytest.mark.asyncio
async def test_list_actors_with_pagination(temp_db):
    """Test listing actors with pagination."""
    authors = [Actor(slug=f"actor-{i}", name=f"Author {i}") for i in range(5)]

    for author in authors:
        await temp_db.put_author(actor)

    result = await temp_db.list_actors(limit=2, offset=1)
    assert len(result) == 2
