import pytest
from interviewos.models import JobProfile, SkillRequirement
from interviewos.interview.strategies.technical import (
    TechnicalCompetency,
    TechnicalInterviewBlueprint,
    TechnicalBlueprintGenerator,
    TechnicalQuestionGenerator,
    TechnicalQuestion,
    QuestionType
)
from unittest.mock import AsyncMock
from interviewos.interview.session import InterviewSession, InterviewType, DepthLevel, Misconception, AnswerAssessment

@pytest.mark.asyncio
async def test_blueprint_generator():
    mock_llm = AsyncMock()
    _mock_ret = '''{
        "role": "AI Engineer",
        "competencies": [
            {
                "name": "PyTorch",
                "importance": 0.9,
                "required": true,
                "topics": ["autograd", "training loop"]
            }
        ],
        "priority": {"PyTorch": "HIGH"}
    }'''
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        return model(**json.loads(_mock_ret))
    mock_llm.generate_structured.side_effect = _generate_structured_wrapper
    
    generator = TechnicalBlueprintGenerator(mock_llm)
    job = JobProfile(title="AI Engineer")
    blueprint = await generator.generate(job)
    
    assert blueprint.role == "AI Engineer"
    assert len(blueprint.competencies) == 1
    assert blueprint.competencies[0].name == "PyTorch"
    assert blueprint.priority["PyTorch"] == "HIGH"

@pytest.mark.asyncio
async def test_question_generator():
    mock_llm = AsyncMock()
    _mock_ret = '''{
        "competency": "PyTorch",
        "topic": "autograd",
        "question_type": "mechanism",
        "question_text": "What happens during loss.backward()?"
    }'''
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        return model(**json.loads(_mock_ret))
    mock_llm.generate_structured.side_effect = _generate_structured_wrapper
    
    generator = TechnicalQuestionGenerator(mock_llm)
    job = JobProfile(title="AI Engineer")
    question = await generator.generate(job, "PyTorch", "autograd", "medium", "")
    
    assert question.question_type == QuestionType.MECHANISM
    assert question.question_text == "What happens during loss.backward()?"

def test_session_models():
    # Verify new models work correctly
    assessment = AnswerAssessment(
        score=0.8,
        strengths=["Good understanding"],
        technical_correctness_score=0.9,
        conceptual_depth_score=0.7,
        misconceptions=[
            Misconception(concept="Gradient", misconception="It updates weights", correction="It computes gradients")
        ],
        demonstrated_depth=DepthLevel.INTERMEDIATE
    )
    
    assert assessment.technical_correctness_score == 0.9
    assert len(assessment.misconceptions) == 1
    assert assessment.demonstrated_depth == DepthLevel.INTERMEDIATE
