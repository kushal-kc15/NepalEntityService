"""Unit tests for FileDatabase actor operations."""

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
def sample_actor():
    """Create a sample actor for testing."""
    return Actor(slug="harka-sampang", name="Harka Sampang")


@pytest.mark.asyncio
async def test_put_actor(temp_db, sample_actor):
    """Test putting an actor."""
    result = await temp_db.put_actor(sample_actor)
    assert result == sample_actor

    # Verify file exists
    file_path = temp_db._id_to_path(sample_actor.id)
    assert file_path.exists()


@pytest.mark.asyncio
async def test_get_actor(temp_db, sample_actor):
    """Test getting an actor."""
    await temp_db.put_actor(sample_actor)
    result = await temp_db.get_actor(sample_actor.id)
    assert result.slug == sample_actor.slug
    assert result.name == sample_actor.name


@pytest.mark.asyncio
async def test_get_nonexistent_actor(temp_db):
    """Test getting a non-existent actor."""
    result = await temp_db.get_actor("actor:nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_actor(temp_db, sample_actor):
    """Test deleting an actor."""
    await temp_db.put_actor(sample_actor)
    result = await temp_db.delete_actor(sample_actor.id)
    assert result is True

    # Verify file is deleted
    file_path = temp_db._id_to_path(sample_actor.id)
    assert not file_path.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_actor(temp_db):
    """Test deleting a non-existent actor."""
    result = await temp_db.delete_actor("actor:nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_list_actors(temp_db):
    """Test listing actors."""
    actors = [
        Actor(slug="harka-sampang", name="Harka Sampang"),
        Actor(slug="rabindra-mishra", name="Rabindra Mishra"),
    ]

    for actor in actors:
        await temp_db.put_actor(actor)

    result = await temp_db.list_actors()
    assert len(result) == 2
    assert all(isinstance(actor, Actor) for actor in result)


@pytest.mark.asyncio
async def test_list_actors_with_pagination(temp_db):
    """Test listing actors with pagination."""
    actors = [Actor(slug=f"actor-{i}", name=f"Actor {i}") for i in range(5)]

    for actor in actors:
        await temp_db.put_actor(actor)

    result = await temp_db.list_actors(limit=2, offset=1)
    assert len(result) == 2
