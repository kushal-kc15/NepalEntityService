"""Tests for base models in nes2."""

import pytest
from pydantic import ValidationError


def test_name_requires_at_least_one_language():
    """Test that Name model requires at least one language."""
    from nes2.core.models.base import Name, NameKind
    
    # Should fail without any language
    with pytest.raises(ValidationError):
        Name(kind=NameKind.PRIMARY)
    
    # Should succeed with English only
    name = Name(
        kind=NameKind.PRIMARY,
        en={"full": "Ram Chandra Poudel"}
    )
    assert name.en.full == "Ram Chandra Poudel"
    
    # Should succeed with Nepali only
    name = Name(
        kind=NameKind.PRIMARY,
        ne={"full": "राम चन्द्र पौडेल"}
    )
    assert name.ne.full == "राम चन्द्र पौडेल"
    
    # Should succeed with both languages
    name = Name(
        kind=NameKind.PRIMARY,
        en={"full": "Ram Chandra Poudel"},
        ne={"full": "राम चन्द्र पौडेल"}
    )
    assert name.en.full == "Ram Chandra Poudel"
    assert name.ne.full == "राम चन्द्र पौडेल"


def test_name_parts_structure():
    """Test NameParts model structure."""
    from nes2.core.models.base import NameParts
    
    # Minimal name with just full
    name_parts = NameParts(full="Ram Chandra Poudel")
    assert name_parts.full == "Ram Chandra Poudel"
    assert name_parts.first is None
    
    # Complete name with all parts
    name_parts = NameParts(
        full="Ram Chandra Poudel",
        first="Ram Chandra",
        last="Poudel"
    )
    assert name_parts.full == "Ram Chandra Poudel"
    assert name_parts.first == "Ram Chandra"
    assert name_parts.last == "Poudel"


def test_contact_validation():
    """Test Contact model validation."""
    from nes2.core.models.base import Contact, ContactType
    
    # Valid email
    contact = Contact(type=ContactType.EMAIL, value="test@example.com")
    assert contact.type == ContactType.EMAIL
    
    # Invalid email should fail
    with pytest.raises(ValidationError):
        Contact(type=ContactType.EMAIL, value="not-an-email")
    
    # Valid phone (E.164 format)
    contact = Contact(type=ContactType.PHONE, value="+9779841234567")
    assert contact.type == ContactType.PHONE
    
    # Invalid phone should fail
    with pytest.raises(ValidationError):
        Contact(type=ContactType.PHONE, value="123456")


def test_lang_text_structure():
    """Test LangText model structure."""
    from nes2.core.models.base import LangText, LangTextValue, ProvenanceMethod
    
    # English only
    text = LangText(
        en=LangTextValue(value="Description in English", provenance=ProvenanceMethod.HUMAN)
    )
    assert text.en.value == "Description in English"
    assert text.en.provenance == ProvenanceMethod.HUMAN
    
    # Both languages
    text = LangText(
        en=LangTextValue(value="English", provenance=ProvenanceMethod.HUMAN),
        ne=LangTextValue(value="नेपाली", provenance=ProvenanceMethod.LLM)
    )
    assert text.en.value == "English"
    assert text.ne.value == "नेपाली"
