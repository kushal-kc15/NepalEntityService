"""Base models using Pydantic."""

from typing import Optional

from pydantic import BaseModel


class CursorPage(BaseModel):
    after: Optional[str] = None
    hasMore: bool


class Name(BaseModel):
    value: str
    lang: str


class ContactInfo(BaseModel):
    type: str
    value: str
    label: Optional[str] = None
