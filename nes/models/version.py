"""Version models using Pydantic."""

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


class Actor(BaseModel):
    id: str
    name: Optional[str] = None


class Version(BaseModel):
    id: str
    versionNumber: int
    actor: Actor
    changeDescription: str
    date: datetime


VersionType = Literal["ENTITY", "RELATIONSHIP"]


class VersionDetails(Version):
    type: VersionType
    createdAt: Optional[datetime] = None
    changes: Optional[Dict[str, Any]] = None
