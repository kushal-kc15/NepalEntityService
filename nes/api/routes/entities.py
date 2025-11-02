"""Entity endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

from nes.models import CursorPage, Entity, EntityType

router = APIRouter(tags=["Entities"])


class EntityListResponse(BaseModel):
    results: List[Entity]
    page: CursorPage


@router.get("/entities", response_model=EntityListResponse)
async def list_entities(
    q: Optional[str] = Query(None, description="Search query"),
    type: Optional[EntityType] = Query(None),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List/search entities."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/{id}", response_model=Entity)
async def get_entity(id: str = Path(..., description="UUID")):
    """Get an entity by ID."""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/{id}/versions/{versionNumber}", response_model=Entity)
async def get_entity_version(
    id: str = Path(..., description="UUID"), versionNumber: int = Path(...)
):
    """Get entity at a specific version."""
    raise HTTPException(status_code=501, detail="Not implemented")
