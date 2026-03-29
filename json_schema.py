#!/usr/bin/env python3
"""json_schema: JSON Schema validator (subset of Draft 7)."""
import re, sys

def validate(instance, schema):
    errors = []
    _validate(instance, schema, "", errors)
    return errors

def _validate(inst, schema, path, errors):
    if not isinstance(schema, dict): return
    # Type check
    if "type" in schema:
        expected = schema["type"]
        type_map = {"string": str, "number": (int, float), "integer": int,
                     "boolean": bool, "array": list, "object": dict, "null": type(None)}
        if expected in type_map:
            t = type_map[expected]
            if not isinstance(inst, t) or (expected == "integer" and isinstance(inst, bool)):
                errors.append(f"{path}: expected {expected}, got {type(inst).__name__}")
                return
    # String constraints
    if isinstance(inst, str):
        if "minLength" in schema and len(inst) < schema["minLength"]:
            errors.append(f"{path}: minLength {schema['minLength']}")
        if "maxLength" in schema and len(inst) > schema["maxLength"]:
            errors.append(f"{path}: maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            errors.append(f"{path}: pattern mismatch")
    # Number constraints
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            errors.append(f"{path}: minimum {schema['minimum']}")
        if "maximum" in schema and inst > schema["maximum"]:
            errors.append(f"{path}: maximum {schema['maximum']}")
    # Array
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errors.append(f"{path}: minItems {schema['minItems']}")
        if "maxItems" in schema and len(inst) > schema["maxItems"]:
            errors.append(f"{path}: maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, item in enumerate(inst):
                _validate(item, schema["items"], f"{path}[{i}]", errors)
    # Object
    if isinstance(inst, dict):
        if "required" in schema:
            for req in schema["required"]:
                if req not in inst:
                    errors.append(f"{path}: missing required '{req}'")
        if "properties" in schema:
            for key, sub_schema in schema["properties"].items():
                if key in inst:
                    _validate(inst[key], sub_schema, f"{path}.{key}", errors)
    # Enum
    if "enum" in schema and inst not in schema["enum"]:
        errors.append(f"{path}: not in enum {schema['enum']}")

def test():
    schema = {
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "tags": {"type": "array", "items": {"type": "string"}},
        }
    }
    assert validate({"name": "Alice", "age": 30}, schema) == []
    assert validate({"name": "Alice", "age": 30, "tags": ["a", "b"]}, schema) == []
    # Missing required
    errs = validate({"name": "Alice"}, schema)
    assert any("missing required" in e for e in errs)
    # Wrong type
    errs = validate({"name": "Alice", "age": "thirty"}, schema)
    assert any("expected integer" in e for e in errs)
    # Constraint violation
    errs = validate({"name": "", "age": -1}, schema)
    assert len(errs) >= 2
    # Enum
    s2 = {"type": "string", "enum": ["red", "green", "blue"]}
    assert validate("red", s2) == []
    assert len(validate("yellow", s2)) > 0
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: json_schema.py test")
