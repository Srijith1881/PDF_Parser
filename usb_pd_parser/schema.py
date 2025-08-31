from __future__ import annotations

from typing import Any, Dict, Tuple

from jsonschema import Draft7Validator

TOC_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "doc_title",
        "section_id",
        "title",
        "full_path",
        "page",
        "level",
    ],
    "properties": {
        "doc_title": {"type": "string"},
        "section_id": {"type": "string"},
        "title": {"type": "string"},
        "full_path": {"type": "string"},
        "page": {"type": "integer", "minimum": 1},
        "level": {"type": "integer", "minimum": 1},
        "parent_id": {"type": ["string", "null"]},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}

SECTION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["doc_title", "section_id", "title", "full_path", "page", "level", "text"],
    "properties": {
        "doc_title": {"type": "string"},
        "section_id": {"type": "string"},
        "title": {"type": "string"},
        "full_path": {"type": "string"},
        "page": {"type": "integer", "minimum": 1},
        "level": {"type": "integer", "minimum": 1},
        "parent_id": {"type": ["string", "null"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "text": {"type": "string"},
    },
}

METADATA_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["doc_title", "type", "id", "title", "page"],
    "properties": {
        "doc_title": {"type": "string"},
        "type": {"type": "string", "enum": ["table", "figure", "note"]},
        "id": {"type": "string"},
        "title": {"type": "string"},
        "page": {"type": "integer", "minimum": 1},
        "section_id": {"type": ["string", "null"]},
    },
}


def validate_item(item: dict, schema: Dict[str, Any]) -> Tuple[bool, str | None]:
    validator = Draft7Validator(schema)
    errs = sorted(validator.iter_errors(item), key=lambda e: e.path)
    if errs:
        return False, errs[0].message
    return True, None
