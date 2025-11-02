"""Version endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel

from nes.models import CursorPage, VersionDetails

router = APIRouter(tags=["Versions"])


class VersionListResponse(BaseModel):
    results: List[VersionDetails]
    page: CursorPage


@router.get("/versions/{id}", response_model=VersionListResponse)
async def list_versions(
    id: str = Path(..., description="UUID"),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
):
    """List versions for an entity."""
    raise HTTPException(status_code=501, detail="Not implemented")
