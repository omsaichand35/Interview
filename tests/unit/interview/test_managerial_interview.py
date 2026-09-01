import pytest
from unittest.mock import AsyncMock
from interviewos.models import JobProfile
from interviewos.interview.strategies.managerial import (
    ManagerialBlueprintGenerator,
    ManagerialQuestionGenerator,
    ManagerialInterviewBlueprint,
    ManagerialCompetency,
    ManagerialQuestionTarget
)

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_blueprint_generator(mock_llm_client):
    _mock_ret = '''{
        "targets": [
            {
                "competency": "Delegation",
                "priority": 1,
                "rationale": "Crucial for scaling."
            }
        ],
        "duration_minutes": 30,
        "total_questions": 5
    }'''
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        return model(**json.loads(_mock_ret))
    mock_llm_client.generate_structured.side_effect = _generate_structured_wrapper
    
    generator = ManagerialBlueprintGenerator(mock_llm_client)
    job = JobProfile(title="Engineering Manager")
    
    blueprint = await generator.generate(job)
    assert len(blueprint.targets) == 1
    assert blueprint.targets[0].competency == ManagerialCompetency.DELEGATION
    assert blueprint.duration_minutes == 30

@pytest.mark.asyncio
async def test_question_generator(mock_llm_client):
    mock_llm_client.generate.return_value = "Tell me about a time you delegated a critical task."
    
    generator = ManagerialQuestionGenerator(mock_llm_client)
    job = JobProfile(title="Engineering Manager")
    
    q = await generator.generate(job, ManagerialCompetency.DELEGATION, "")
    assert "delegated" in q
