# schema.py
"""
JSON schema definitions and helper validators.
We keep schemas simple and provide a helper to validate dictionaries with jsonschema.
"""

from jsonschema import validate as js_validate, ValidationError

TOC_SCHEMA = {
    "type": "object",
    "properties": {
        "doc_title": {"type": "string"},
        "section_id": {"type": "string"},
        "title": {"type": "string"},
        "full_path": {"type": "string"},
        "page": {"type": "integer", "minimum": 1},
        "level": {"type": "integer", "minimum": 1},
        "parent_id": {"type": ["string", "null"]},
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["doc_title", "section_id", "title", "full_path", "page", "level"]
}

SECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "doc_title": {"type": "string"},
        "section_id": {"type": "string"},
        "title": {"type": "string"},
        "full_path": {"type": "string"},
        "start_page": {"type": "integer", "minimum": 1},
        "end_page": {"type": "integer", "minimum": 1},
        "text": {"type": "string"},
        "level": {"type": "integer", "minimum": 1},
        "parent_id": {"type": ["string", "null"]},
        "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["doc_title", "section_id", "title", "full_path", "start_page", "end_page", "text"]
}

METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "doc_title": {"type": "string"},
        "type": {"type": "string"},
        "id": {"type": "string"},
        "title": {"type": ["string", "null"]},
        "page": {"type": "integer", "minimum": 1}
    },
    "required": ["doc_title", "type", "id", "page"]
}

def validate_item(item: dict, schema: dict) -> tuple[bool,str]:
    try:
        js_validate(instance=item, schema=schema)
        return True, ""
    except ValidationError as e:
        return False, str(e)
