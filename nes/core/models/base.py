"""Base models using Pydantic."""

from typing import Optional

from pydantic import BaseModel, Field


class CursorPage(BaseModel):
    hasMore: bool
    offset: int = 0


class Name(BaseModel):
    """Represents a name with language and kind classification."""

    value: str = Field(..., description="The actual name string")

    lang: str = Field(..., description="Language code for the name")

    kind: str = Field(
        ...,
        min_length=3,
        max_length=15,
        description="Type of name (DEFAULT, FIRST_NAME, LAST_NAME, etc.)",
    )


class ContactInfo(BaseModel):
    type: str
    value: str
    label: Optional[str] = None
