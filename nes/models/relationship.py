"""Relationship model using Pydantic."""

from datetime import date, datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

from .version import Version

RelationshipType = Literal[
    "AFFILIATED_WITH",
    "EMPLOYED_BY",
    "MEMBER_OF",
    "PARENT_OF",
    "CHILD_OF",
    "SUPERVISES",
    "LOCATED_IN",
]


class Relationship(BaseModel):
    id: str
    sourceEntityId: str
    targetEntityId: str
    type: RelationshipType
    versionInfo: Version
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    attributes: Optional[Dict[str, Any]] = None
    createdAt: Optional[datetime] = None
