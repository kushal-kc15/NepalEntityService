"""Relationship endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException, Path

from nes.models import Relationship

router = APIRouter(tags=["Relationships"])


@router.get("/entities/{id}/relationships", response_model=List[Relationship])
async def get_entity_relationships(id: str = Path(..., description="UUID")):
    """List relationships for an entity."""
    raise HTTPException(status_code=501, detail="Not implemented")
