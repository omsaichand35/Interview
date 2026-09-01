import json
import re
from typing import TypeVar
import json_repair

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class StructuredOutputError(Exception):
    """Raised when an LLM response cannot be converted to a model."""

    pass


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


def parse_structured_output(
    response: str,
    model: type[T],
) -> T:
    """
    Parse an LLM response into a validated Pydantic model with automatic JSON repair.
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
                    f"LLM response is not valid JSON. Raw text was: {repr(response)}\nExtracted text was: {repr(json_text)}"
                ) from exc

    if not isinstance(data, dict):
        raise StructuredOutputError(
            f"Expected JSON object for {model.__name__}, got {type(data).__name__}: {repr(data)}"
        )

    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise StructuredOutputError(
            f"LLM response does not match {model.__name__}: {exc}"
        ) from exc