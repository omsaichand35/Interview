import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel

from interviewos.llm.client import LLMClient
from interviewos.core.exceptions import LLMUnavailableError, InvalidLLMResponseError

class DummyModel(BaseModel):
    name: str
    age: int

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    return provider

@pytest.fixture
def llm_client(mock_provider):
    # Pass a real mock provider to the LLMClient so we can test generate_structured
    client = LLMClient(mock_provider)
    return client

@pytest.mark.asyncio
async def test_generate_structured_success(llm_client, mock_provider):
    mock_provider.generate.return_value = '{"name": "Alice", "age": 30}'
    
    result = await llm_client.generate_structured(prompt="Who are you?", model=DummyModel)
    
    assert result.name == "Alice"
    assert result.age == 30
    assert mock_provider.generate.call_count == 1

@pytest.mark.asyncio
async def test_generate_structured_validation_repair(llm_client, mock_provider):
    # First attempt: Invalid JSON (missing age)
    # Second attempt: Valid JSON
    mock_provider.generate.side_effect = [
        '{"name": "Alice"}',
        '{"name": "Alice", "age": 30}'
    ]
    
    result = await llm_client.generate_structured(prompt="Who are you?", model=DummyModel)
    
    assert result.name == "Alice"
    assert result.age == 30
    assert mock_provider.generate.call_count == 2
    
    # Verify the second prompt contained the repair instructions
    second_call_args = mock_provider.generate.call_args_list[1]
    prompt_used = second_call_args.kwargs.get("prompt")
    assert prompt_used is not None
    assert "failed validation with the following error" in prompt_used

@pytest.mark.asyncio
async def test_generate_structured_exhaust_retries(llm_client, mock_provider):
    # Always returns invalid schema
    mock_provider.generate.return_value = '{"name": "Alice"}'
    
    with pytest.raises(InvalidLLMResponseError) as exc:
        await llm_client.generate_structured(prompt="Who are you?", model=DummyModel, max_retries=2)
        
    assert "Failed to validate LLM response after 2 attempts" in str(exc.value)
    assert mock_provider.generate.call_count == 2

@pytest.mark.asyncio
async def test_generate_structured_timeout(llm_client, mock_provider):
    # Simulate a timeout
    async def sleep_generate(*args, **kwargs):
        await asyncio.sleep(0.5)
        return '{"name": "Alice", "age": 30}'
        
    mock_provider.generate.side_effect = sleep_generate
    
    with pytest.raises(LLMUnavailableError) as exc:
        # Timeout is 0.1s, mock sleeps for 0.5s
        await llm_client.generate_structured(prompt="Who are you?", model=DummyModel, timeout_seconds=0.1)
        
    assert "timed out" in str(exc.value)

