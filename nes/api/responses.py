"""API response models."""

from typing import List

from pydantic import BaseModel


class SchemaListResponse(BaseModel):
    types: List[str]
