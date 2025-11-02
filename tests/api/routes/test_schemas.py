"""Test cases for /schemas APIs."""

from fastapi.testclient import TestClient

from nes.api import app
from nes.models import Entity, Person

client = TestClient(app)


def test_list_schemas():
    """Test GET /schemas returns list of entity types."""
    response = client.get("/schemas")
    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert data["types"] == ["PERSON", "ORGANIZATION", "GOV_BODY"]


def test_get_person_schema():
    """Test GET /schemas/PERSON returns Person JSON schema."""
    response = client.get("/schemas/PERSON")
    assert response.status_code == 200

    expected_schema = Person.model_json_schema()
    schema = response.json()

    assert schema == expected_schema


def test_get_organization_schema():
    """Test GET /schemas/ORGANIZATION returns Entity JSON schema."""
    response = client.get("/schemas/ORGANIZATION")
    assert response.status_code == 200

    expected_schema = Entity.model_json_schema()
    schema = response.json()

    assert schema == expected_schema


def test_get_gov_body_schema():
    """Test GET /schemas/GOV_BODY returns Entity JSON schema."""
    response = client.get("/schemas/GOV_BODY")
    assert response.status_code == 200

    expected_schema = Entity.model_json_schema()
    schema = response.json()

    assert schema == expected_schema


def test_get_invalid_schema():
    """Test GET /schemas/{invalid_type} returns 422."""
    response = client.get("/schemas/INVALID")
    assert response.status_code == 422
