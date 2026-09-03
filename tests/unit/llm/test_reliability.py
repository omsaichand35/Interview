import json
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel

from interviewos.llm.client import LLMClient
from interviewos.core.exceptions import LLMUnavailableError, InvalidLLMResponseError, LLMRateLimitError

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

@pytest.mark.asyncio
async def test_generate_structured_rate_limit_retry_success(llm_client, mock_provider):
    mock_provider.generate.side_effect = [
        LLMRateLimitError("Too Many Requests"),
        '{"name": "Bob", "age": 25}'
    ]
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await llm_client.generate_structured(prompt="Who are you?", model=DummyModel, max_retries=3)
        assert result.name == "Bob"
        assert result.age == 25
        assert mock_provider.generate.call_count == 2
        assert mock_sleep.call_count == 1

@pytest.mark.asyncio
async def test_generate_structured_rate_limit_exhaust(llm_client, mock_provider):
    mock_provider.generate.side_effect = LLMRateLimitError("Too Many Requests")
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(LLMUnavailableError) as exc:
            await llm_client.generate_structured(prompt="Who are you?", model=DummyModel, max_retries=2)
            
        assert "rate limits" in str(exc.value)
        assert mock_provider.generate.call_count == 2
        assert mock_sleep.call_count == 1


def test_parse_structured_output_interview_decision_class_keys():
    from interviewos.llm.structured_output import parse_structured_output
    from interviewos.interview.session import InterviewDecision, InterviewAction, DifficultyChange

    raw_response = '''
    {
      "AnswerAssessment": {
        "score": 0.75,
        "strengths": ["Good architectural knowledge"],
        "weaknesses": ["Needs more performance details"]
      },
      "InterviewAction": "ask_follow_up",
      "DifficultyChange": "same"
    }
    '''
    decision = parse_structured_output(raw_response, InterviewDecision)
    assert decision.assessment.score == 0.75
    assert decision.action == InterviewAction.ASK_FOLLOW_UP
    assert decision.difficulty_change == DifficultyChange.SAME
    assert decision.assessment.strengths == ["Good architectural knowledge"]


@pytest.mark.parametrize(
    "evidence_item",
    [
        "The candidate described the tool-calling architecture.",
        {
            "type": "text",
            "text": "The candidate described the tool-calling architecture.",
        },
    ],
)
def test_parse_structured_output_normalizes_text_question_evidence(evidence_item):
    from interviewos.llm.structured_output import parse_structured_output
    from interviewos.interview.session import InterviewDecision

    raw_response = {
        "assessment": {"score": 0.8},
        "question_evidence": [evidence_item],
    }

    decision = parse_structured_output(json.dumps(raw_response), InterviewDecision)

    assert len(decision.question_evidence) == 1
    assert decision.question_evidence[0].evidence.startswith("The candidate")
    assert decision.question_evidence[0].reason == ""


def test_parse_structured_output_job_profile_list_unwrapping():
    from interviewos.llm.structured_output import parse_structured_output
    from interviewos.models import JobProfile

    raw_response = '''
    [
      {
        "title": "Senior Backend Engineer",
        "company": "Tech Corp",
        "required_skills": []
      }
    ]
    '''
    job = parse_structured_output(raw_response, JobProfile)
    assert job.title == "Senior Backend Engineer"
    assert job.company == "Tech Corp"


def test_parse_structured_output_job_profile_normalizes_string_lists_from_objects():
    """Test that qualifications and interview_topics lists of objects are normalized to strings."""
    from interviewos.llm.structured_output import parse_structured_output
    from interviewos.models import JobProfile

    # LLM returns objects with 'name' field instead of plain strings
    raw_response = '''
    {
      "title": "Senior Backend Engineer",
      "company": "Tech Corp",
      "qualifications": [
        {"name": "Bachelor's degree in CS", "importance": 1.0},
        {"name": "5+ years experience", "importance": 0.9}
      ],
      "interview_topics": [
        {"name": "System Design", "importance": 1.0},
        {"name": "Python", "importance": 1.0}
      ],
      "required_skills": [],
      "preferred_skills": [],
      "responsibilities": []
    }
    '''
    job = parse_structured_output(raw_response, JobProfile)
    assert job.title == "Senior Backend Engineer"
    # Verify that string lists were extracted from objects
    assert job.qualifications == ["Bachelor's degree in CS", "5+ years experience"]
    assert job.interview_topics == ["System Design", "Python"]


def test_parse_structured_output_job_responsibility_name_to_description():
    """Test that responsibility 'name' field is mapped to 'description'."""
    from interviewos.llm.structured_output import parse_structured_output
    from interviewos.models import JobProfile

    raw_response = '''
    {
      "title": "Senior Backend Engineer",
      "responsibilities": [
        {"name": "Design scalable systems", "skills": ["Python", "System Design"]},
        {"name": "Mentor junior developers", "skills": ["Leadership"]}
      ],
      "required_skills": [],
      "preferred_skills": [],
      "qualifications": [],
      "interview_topics": []
    }
    '''
    job = parse_structured_output(raw_response, JobProfile)
    assert job.title == "Senior Backend Engineer"
    assert len(job.responsibilities) == 2
    # Verify that 'name' was mapped to 'description'
    assert job.responsibilities[0].description == "Design scalable systems"
    assert job.responsibilities[1].description == "Mentor junior developers"
    assert job.responsibilities[0].skills == ["Python", "System Design"]
    assert job.responsibilities[1].skills == ["Leadership"]




