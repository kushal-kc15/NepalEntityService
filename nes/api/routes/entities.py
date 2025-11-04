"""Entity endpoints."""

import json
from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from nes.core.identifiers import build_version_id
from nes.core.models import CursorPage, Entity, EntityType
from nes.database import EntityDatabase
from nes.database import get_database as get_db

router = APIRouter(tags=["Entities"])


def get_database() -> EntityDatabase:
    """Get database instance."""
    return get_db()


class EntityListResponse(BaseModel):
    results: List[Entity]
    page: CursorPage


@router.get("/entities", response_model=EntityListResponse)
async def entities(
    id: Optional[str] = Query(
        None,
        description="Entity ID in format `entity:type:subtype:slug` (e.g., `entity:person:politician:harka-sampang`, `entity:organization:party:rastriya-swatantra-party`)",
    ),
    version: Optional[int] = Query(
        None,
        description="Retrieve a specific entity version - requires the id parameter to be set",
    ),
    q: Optional[str] = Query(None, description="Search query - not implemented"),
    type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    subtype: Optional[str] = Query(
        None, description="Filter by entity subtype (e.g., 'politician', 'party')"
    ),
    attributes: Optional[str] = Query(
        None,
        description='Filter by attributes as JSON string with key-value pairs. Multiple attributes are combined using AND logic (e.g., `{"sys:governmentType":"state","sys:status":"active"}`)',
    ),
    limit: int = Query(20, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset (Number of items to skip)"),
    db: EntityDatabase = Depends(get_database),
):
    """Get entity by ID, specific version, or list/search entities."""
    if version is not None and id is None:
        raise HTTPException(
            status_code=400, detail="Version parameter requires id parameter"
        )

    if id:
        if version is not None:
            version_id = build_version_id(id, version)
            version_obj = await db.get_version(version_id)
            if not version_obj or not version_obj.snapshot:
                raise HTTPException(status_code=404, detail="Entity version not found")
            entity = Entity.model_validate(version_obj.snapshot)
        else:
            entity = await db.get_entity(id)
            if not entity:
                raise HTTPException(status_code=404, detail="Entity not found")
        return EntityListResponse(
            results=[entity], page=CursorPage(hasMore=False, offset=0, count=1)
        )

    if q:
        raise HTTPException(status_code=501, detail="Search query not implemented")

    # Parse attribute filters
    attr_filters = None
    if attributes:
        try:
            attr_filters = json.loads(attributes)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid JSON format for attributes"
            )

    entities = await db.list_entities(
        limit=limit,
        offset=offset,
        type=type,
        subtype=subtype,
        attr_filters=attr_filters,
    )
    return EntityListResponse(
        results=entities,
        page=CursorPage(
            hasMore=len(entities) == limit, offset=offset, count=len(entities)
        ),
    )
