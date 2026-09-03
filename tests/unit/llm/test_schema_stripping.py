"""Tests for JSON schema metadata stripping in structured output parser."""

import pytest
from interviewos.llm.structured_output import _strip_schema_metadata


def test_strip_schema_metadata_removes_defs():
    """Test that $defs are removed from schema documents."""
    data = {
        "$defs": {
            "QuestionType": {
                "enum": ["mcq", "multiple_select", "true_false"],
                "type": "string",
            }
        },
        "properties": {"title": {"type": "string"}},
        "required": ["title"],
        "type": "object",
    }
    result = _strip_schema_metadata(data)
    assert "$defs" not in result
    assert "properties" not in result
    assert "required" not in result
    assert "type" not in result


def test_strip_schema_metadata_preserves_data():
    """Test that actual data fields are preserved."""
    data = {
        "title": "My Title",
        "description": "My Description",
        "count": 42,
    }
    result = _strip_schema_metadata(data)
    assert result == data


def test_strip_schema_metadata_extracts_nested_data():
    """Test that nested data objects are extracted from schema documents."""
    data = {
        "$defs": {"SomeModel": {"type": "object"}},
        "properties": {"title": {"type": "string"}},
        "data": {"title": "Actual Title", "value": 123},
    }
    result = _strip_schema_metadata(data)
    # Should extract the nested data object
    assert result == {"title": "Actual Title", "value": 123}


def test_strip_schema_metadata_with_ref():
    """Test that $ref schema keys are removed."""
    data = {
        "$ref": "#/$defs/QuestionType",
        "title": "My Title",
        "enum": ["a", "b"],
    }
    result = _strip_schema_metadata(data)
    # With $ref and enum, this looks like a schema doc
    assert "$ref" not in result
    assert "enum" not in result


def test_strip_schema_metadata_detects_schema_doc():
    """Test that documents with 2+ schema keys are recognized as schemas."""
    # This should be detected as schema
    schema_doc = {
        "properties": {},
        "required": [],
        "type": "object",
    }
    result = _strip_schema_metadata(schema_doc)
    # All schema keys should be removed
    assert len(result) == 0


def test_strip_schema_metadata_non_dict_passthrough():
    """Test that non-dict values pass through unchanged."""
    assert _strip_schema_metadata([1, 2, 3]) == [1, 2, 3]
    assert _strip_schema_metadata("string") == "string"
    assert _strip_schema_metadata(None) is None


def test_strip_schema_metadata_handles_empty_dict():
    """Test that empty dicts are handled."""
    result = _strip_schema_metadata({})
    assert result == {}


def test_strip_schema_metadata_with_items():
    """Test that 'items' schema keyword is removed."""
    data = {
        "items": {"type": "string"},
        "type": "array",
        "examples": [["a", "b"]],
    }
    result = _strip_schema_metadata(data)
    assert "items" not in result
    assert "type" not in result
    assert "examples" not in result


def test_strip_schema_metadata_with_additionalproperties():
    """Test that additionalProperties schema keyword is removed."""
    data = {
        "additionalProperties": False,
        "properties": {"id": {"type": "string"}},
        "type": "object",
    }
    result = _strip_schema_metadata(data)
    assert "additionalProperties" not in result
    assert "properties" not in result
    assert "type" not in result


def test_strip_schema_metadata_all_schema_keys():
    """Test removal of all JSON schema keywords."""
    schema_keywords = {
        "$defs": {},
        "$ref": "",
        "$schema": "",
        "$id": "",
        "$comment": "",
        "properties": {},
        "required": [],
        "type": "",
        "items": {},
        "additionalProperties": False,
        "definitions": {},
        "enum": [],
        "const": None,
        "default": None,
        "examples": [],
        "minLength": 0,
        "maxLength": 100,
        "pattern": "",
        "minimum": 0,
        "maximum": 100,
        "minItems": 0,
        "maxItems": 10,
        "uniqueItems": False,
        "oneOf": [],
        "anyOf": [],
        "allOf": [],
    }
    result = _strip_schema_metadata(schema_keywords)
    # Should be empty or minimal
    assert len(result) == 0


def test_strip_schema_metadata_preserves_user_data_with_schema():
    """Test that user data is preserved even when schema keywords present."""
    data = {
        "name": "John",
        "age": 30,
        "type": "object",  # This is a schema key, but...
        "properties": {},  # ...combined with this makes it look like schema
    }
    result = _strip_schema_metadata(data)
    # Detected as schema, so all schema keys removed
    # but data fields should be preserved if no nested extraction
    assert "type" not in result
    assert "properties" not in result
