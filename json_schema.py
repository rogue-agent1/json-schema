#!/usr/bin/env python3
"""json_schema - JSON Schema validator (draft-07 subset)."""
import sys, json, re

def validate(inst, schema, path="$"):
    errors = []
    t = schema.get("type")
    tmap = {"string": str, "number": (int,float), "integer": int, "boolean": bool, "array": list, "object": dict}
    if t and t in tmap and not isinstance(inst, tmap[t]):
        return [f"{path}: expected {t}, got {type(inst).__name__}"]
    if isinstance(inst, str):
        if "minLength" in schema and len(inst) < schema["minLength"]: errors.append(f"{path}: too short")
        if "pattern" in schema and not re.search(schema["pattern"], inst): errors.append(f"{path}: pattern mismatch")
    if isinstance(inst, (int,float)):
        if "minimum" in schema and inst < schema["minimum"]: errors.append(f"{path}: below minimum")
        if "maximum" in schema and inst > schema["maximum"]: errors.append(f"{path}: above maximum")
    if isinstance(inst, list) and "items" in schema:
        for i, item in enumerate(inst): errors.extend(validate(item, schema["items"], f"{path}[{i}]"))
    if isinstance(inst, dict):
        for req in schema.get("required", []):
            if req not in inst: errors.append(f"{path}: missing {req}")
        for prop, ps in schema.get("properties", {}).items():
            if prop in inst: errors.extend(validate(inst[prop], ps, f"{path}.{prop}"))
    return errors

def main():
    schema = {"type":"object","required":["name","age"],"properties":{"name":{"type":"string","minLength":1},"age":{"type":"integer","minimum":0,"maximum":150}}}
    print("JSON Schema validator demo\n")
    for obj in [{"name":"Alice","age":30},{"name":"","age":200},{"age":25},{"name":"Bob","age":"x"}]:
        errs = validate(obj, schema)
        print(f"  {'ok' if not errs else 'FAIL'} {json.dumps(obj)}")
        for e in errs: print(f"    {e}")

if __name__ == "__main__":
    main()
