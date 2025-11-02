"""Person dataclass for Nepal Entity Service."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Person:
    """Represents a person entity."""
    
    id: str
    names: Dict[str, str]
    attributes: Dict[str, Any]
    summary: Optional[str] = None
    description: Optional[str] = None