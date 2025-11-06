"""Schema endpoints."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Path

from nes.api.responses import SchemaListResponse
from nes.core.models import ENTITY_TYPE_MAP, Entity, EntityType, Location, Person

router = APIRouter(tags=["Schemas"])


@router.get("/schemas", response_model=SchemaListResponse)
async def list_schemas():
    """List available entity type schemas."""
    return {"types": list(ENTITY_TYPE_MAP.keys())}


@router.get("/schemas/{type}", response_model=Dict[str, Any])
async def get_schema(type: EntityType = Path(...)):
    """Get JSON Schema for a specific entity type."""
    if type == "person":
        return Person.model_json_schema()
    elif type == "location":
        return Location.model_json_schema()
    elif type in ["organization"]:
        return Entity.model_json_schema()
    raise HTTPException(status_code=404, detail="Schema not found")
