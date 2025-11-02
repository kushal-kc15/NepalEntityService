"""Entity model using Pydantic."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from .base import ContactInfo, Name
from .version import Version

EntityType = Literal["PERSON", "ORGANIZATION", "GOV_BODY"]
ENTITY_TYPES = ["PERSON", "ORGANIZATION", "GOV_BODY"]


class Entity(BaseModel):
    id: str
    type: EntityType
    names: List[Name]
    versionInfo: Version
    createdAt: datetime
    identifiers: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    contacts: Optional[List[ContactInfo]] = None


class Person(BaseModel):
    id: str
    type: Literal["PERSON"]
    names: List[Name] = Field(min_length=1)
    versionInfo: Version
    createdAt: datetime
    identifiers: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    contacts: Optional[List[ContactInfo]] = None
