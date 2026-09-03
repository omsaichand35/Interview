import json
import re
from typing import TypeVar

import json_repair
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class StructuredOutputError(Exception):
    """Raised when an LLM response cannot be converted to a model."""



def _extract_json(response: str) -> str:
    """Extract JSON from a raw LLM response."""

    response = response.strip()

    # Find the outermost JSON object first. This naturally avoids issues
    # where the LLM includes markdown code blocks INSIDE the JSON values.
    start = response.find('{')
    end = response.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        json_str = response[start:end+1]
    else:
        # Fallback for arrays or markdown responses
        fenced_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            response,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced_match:
            json_str = fenced_match.group(1).strip()
        else:
            json_str = response

    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        
    return json_str


def _strip_schema_metadata(data: dict) -> dict:
    """
    Strip JSON schema metadata from LLM response.
    
    Handles cases where LLM returns a JSON Schema document instead of data.
    Removes keys like $defs, $ref, properties, required, type, $schema, etc.
    """
    if not isinstance(data, dict):
        return data
    
    # Keys that indicate schema metadata (from JSON Schema spec)
    schema_keys = {
        "$defs", "$ref", "$schema", "$id", "$comment",
        "properties", "required", "type", "items", "additionalProperties",
        "definitions", "enum", "const", "default", "examples",
        "minLength", "maxLength", "pattern", "minimum", "maximum",
        "minItems", "maxItems", "uniqueItems", "oneOf", "anyOf", "allOf",
    }
    
    # Check if this looks like a schema document
    # (has multiple schema-specific keys)
    schema_key_count = sum(1 for k in data if k in schema_keys)
    is_schema_doc = schema_key_count >= 2 or "$defs" in data or "$ref" in data
    
    if not is_schema_doc:
        return data
    
    # If it's a schema doc, try to extract actual data
    # First, check if there's a nested object that looks like data
    for key, value in data.items():
        if key not in schema_keys and isinstance(value, dict):
            # Found a data object inside the schema
            return _strip_schema_metadata(value)
    
    # Remove all schema keys
    cleaned = {k: v for k, v in data.items() if k not in schema_keys}
    
    return cleaned


def _normalize_dict_keys(data: dict, model: type[BaseModel]) -> dict:
    """Normalize dictionary keys to match Pydantic model field names."""
    if not isinstance(data, dict) or not hasattr(model, "model_fields"):
        return data

    normalized = dict(data)
    
    # Define common field name aliases that LLMs might use
    field_aliases = {
        "description": ["name", "title", "text", "content", "summary", "detail"],
        "title": ["name", "label"],
        "name": ["title", "label"],
    }
    
    # 1. Build map of alias -> field_name for model fields
    field_alias_map = {}
    for field_name, field_info in model.model_fields.items():
        field_alias_map[field_name] = field_name
        field_alias_map[field_name.lower()] = field_name
        
        # PascalCase / TitleCase of field_name
        pascal_field = "".join(word.capitalize() for word in field_name.split("_"))
        field_alias_map[pascal_field] = field_name
        field_alias_map[pascal_field.lower()] = field_name
        
        if getattr(field_info, "alias", None):
            field_alias_map[field_info.alias] = field_name

        target_type = field_info.annotation
        args = getattr(target_type, "__args__", ())
        
        classes_to_check = []
        if isinstance(target_type, type) and target_type not in (str, int, float, bool, list, dict, object):
            classes_to_check.append(target_type)

        if args:
            for arg in args:
                if isinstance(arg, type) and arg not in (str, int, float, bool, list, dict, object):
                    classes_to_check.append(arg)
                    
        for cls_item in classes_to_check:
            cls_name = cls_item.__name__
            field_alias_map[cls_name] = field_name
            field_alias_map[cls_name.lower()] = field_name
            snake_cls = re.sub(r'(?<!^)(?=[A-Z])', '_', cls_name).lower()
            field_alias_map[snake_cls] = field_name
            field_alias_map[snake_cls.lower()] = field_name

    keys_to_process = list(normalized.keys())
    for key in keys_to_process:
        if key not in model.model_fields:
            target_field = field_alias_map.get(key) or field_alias_map.get(key.lower())
            if target_field and target_field not in normalized:
                normalized[target_field] = normalized.pop(key)
    
    # Handle field aliases for missing required fields
    for expected_field, aliases in field_aliases.items():
        if expected_field in model.model_fields and expected_field not in normalized:
            for alias in aliases:
                if alias in normalized:
                    normalized[expected_field] = normalized.pop(alias)
                    break

    # 2. Recursively normalize nested dicts for sub-models
    for field_name, field_info in model.model_fields.items():
        if field_name in normalized:
            val = normalized[field_name]
            target_type = field_info.annotation
            args = getattr(target_type, "__args__", ())
            sub_model = None
            try:
                if isinstance(target_type, type) and issubclass(target_type, BaseModel):
                    sub_model = target_type
            except TypeError:
                pass
            if not sub_model and args:
                for arg in args:
                    try:
                        if isinstance(arg, type) and issubclass(arg, BaseModel):
                            sub_model = arg
                            break
                    except TypeError:
                        pass

            if sub_model and isinstance(val, dict):
                if len(val) == 1:
                    sub_k, sub_v = list(val.items())[0]
                    if isinstance(sub_v, dict) and sub_k.lower() in (sub_model.__name__.lower(), sub_model.__name__.lower().replace("_", "")):
                        val = sub_v
                normalized[field_name] = _normalize_dict_keys(val, sub_model)
            # Handle list[str] fields where LLM returned list[dict] (check this FIRST)
            elif isinstance(val, list) and val and isinstance(val[0], dict):
                # Check if field expects list[str]
                if args and (args[0] is str or args[0] == str):
                    # Extract string values from dicts - try common key names
                    extracted = []
                    for item in val:
                        if isinstance(item, dict):
                            # Try to extract a string value from the dict
                            if "name" in item:
                                extracted.append(item["name"])
                            elif "title" in item:
                                extracted.append(item["title"])
                            elif "description" in item:
                                extracted.append(item["description"])
                            elif "value" in item:
                                extracted.append(item["value"])
                            else:
                                # Last resort: try first string value in dict
                                for v in item.values():
                                    if isinstance(v, str):
                                        extracted.append(v)
                                        break
                        elif isinstance(item, str):
                            extracted.append(item)
                    if extracted:
                        normalized[field_name] = extracted
                # Otherwise, try to normalize as list[BaseModel]
                elif args:
                    for arg in args:
                        try:
                            if isinstance(arg, type) and issubclass(arg, BaseModel):
                                # Normalize each item in list if it's a BaseModel
                                normalized_list = []
                                for item in val:
                                    if isinstance(item, dict):
                                        normalized_list.append(_normalize_dict_keys(item, arg))
                                    else:
                                        normalized_list.append(item)
                                normalized[field_name] = normalized_list
                                break
                        except TypeError:
                            pass
            # Handle list[BaseModel] fields where items might have incorrect field names
            elif isinstance(val, list) and args:
                for arg in args:
                    try:
                        if isinstance(arg, type) and issubclass(arg, BaseModel):
                            # Normalize each item in list if it's a BaseModel
                            normalized_list = []
                            for item in val:
                                if isinstance(item, dict):
                                    normalized_list.append(_normalize_dict_keys(item, arg))
                                else:
                                    normalized_list.append(item)
                            normalized[field_name] = normalized_list
                            break
                    except TypeError:
                        pass

    return normalized


def parse_structured_output(
    response: str,
    model: type[T],
) -> T:
    """
    Parse an LLM response into a validated Pydantic model with automatic JSON repair,
    list unwrapping, outer wrapper unwrapping, and field/class key normalization.
    """
    json_text = _extract_json(response)
    
    # Fix invalid escapes (e.g. \_ or \s) that LLM might hallucinate
    json_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_text)

    data = None
    try:
        data = json.loads(json_text)
    except Exception:
        try:
            data = json_repair.loads(json_text)
        except Exception:
            try:
                data = json_repair.loads(response)
            except Exception as exc:
                raise StructuredOutputError(
                    f"LLM response is not valid JSON. Raw text was: {response!r}\nExtracted text was: {json_text!r}"
                ) from exc

    # Unwrap list if LLM outputted a list of objects
    if isinstance(data, list):
        dict_candidates = [item for item in data if isinstance(item, dict)]
        if not dict_candidates:
            raise StructuredOutputError(
                f"Expected JSON object for {model.__name__}, got list without objects: {data!r}"
            )
        best_candidate = None
        for item in dict_candidates:
            if hasattr(model, "model_fields") and any(k in item for k in model.model_fields):
                best_candidate = item
                break
        if best_candidate is not None:
            data = best_candidate
        else:
            data = dict_candidates[0]

    if not isinstance(data, dict):
        raise StructuredOutputError(
            f"Expected JSON object for {model.__name__}, got {type(data).__name__}: {data!r}"
        )

    # Unwrap single wrapper key (e.g. {"InterviewDecision": {...}} or {"data": {...}})
    if len(data) == 1:
        single_key, single_val = list(data.items())[0]
        if isinstance(single_val, dict):
            key_lower = single_key.lower()
            model_name_lower = model.__name__.lower()
            known_wrappers = {"data", "result", "response", "output", "item", "payload", "decision", "profile", "problem", "blueprint"}
            has_model_fields = hasattr(model, "model_fields") and any(k in single_val for k in model.model_fields)
            if key_lower == model_name_lower or key_lower in known_wrappers or has_model_fields:
                data = single_val

    # Strip JSON schema metadata if present (defense against schema dumps in LLM responses)
    data = _strip_schema_metadata(data)

    # Normalize keys in data dict to match Pydantic model field names
    data = _normalize_dict_keys(data, model)

    try:
        return model.model_validate(data)
    except ValidationError as exc:
        # Fallback: if data contains a nested dict matching model fields, try unwrapping
        for val in data.values():
            if isinstance(val, dict):
                try:
                    norm_val = _normalize_dict_keys(val, model)
                    return model.model_validate(norm_val)
                except ValidationError:
                    pass
        raise StructuredOutputError(
            f"LLM response does not match {model.__name__}: {exc}"
        ) from exc
