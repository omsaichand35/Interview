import pytest
from interviewos.models import JobProfile
from interviewos.interview.strategies.hr import (
    HRCompetency,
    HRInterviewBlueprint,
    HRBlueprintGenerator,
    HRQuestionGenerator,
    HRQuestion,
    HRQuestionType
)
from unittest.mock import AsyncMock
from interviewos.interview.session import InterviewSession, InterviewType, DepthLevel, HREvidence, AnswerAssessment

@pytest.mark.asyncio
async def test_hr_blueprint_generator():
    mock_llm = AsyncMock()
    _mock_ret = '''{
        "role": "AI Engineer",
        "competencies": [
            {
                "name": "Teamwork",
                "importance": 0.9,
                "description": "Works well with others",
                "evidence_requirements": ["STAR structure"]
            }
        ],
        "priority": {"Teamwork": "HIGH"}
    }'''
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        return model(**json.loads(_mock_ret))
    mock_llm.generate_structured.side_effect = _generate_structured_wrapper
    
    generator = HRBlueprintGenerator(mock_llm)
    job = JobProfile(title="AI Engineer")
    blueprint = await generator.generate(job)
    
    assert blueprint.role == "AI Engineer"
    assert len(blueprint.competencies) == 1
    assert blueprint.competencies[0].name == "Teamwork"
    assert blueprint.priority["Teamwork"] == "HIGH"

@pytest.mark.asyncio
async def test_hr_question_generator():
    mock_llm = AsyncMock()
    _mock_ret = '''{
        "competency": "Teamwork",
        "question_type": "behavioral",
        "question_text": "Tell me about a time you worked with a difficult teammate."
    }'''
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        return model(**json.loads(_mock_ret))
    mock_llm.generate_structured.side_effect = _generate_structured_wrapper
    
    generator = HRQuestionGenerator(mock_llm)
    job = JobProfile(title="AI Engineer")
    question = await generator.generate(job, "Teamwork", "")
    
    assert question.question_type == HRQuestionType.BEHAVIORAL
    assert question.question_text == "Tell me about a time you worked with a difficult teammate."

def test_hr_session_models():
    # Verify new models work correctly
    assessment = AnswerAssessment(
        score=0.8,
        hr_relevance_score=0.9,
        hr_communication_score=0.7,
        hr_evidence=[
            HREvidence(situation="Project deadline", task="Build feature", action="I wrote code", result="It worked")
        ],
        demonstrated_depth=DepthLevel.INTERMEDIATE
    )
    
    assert assessment.hr_relevance_score == 0.9
    assert len(assessment.hr_evidence) == 1
    assert assessment.hr_evidence[0].action == "I wrote code"
    assert assessment.demonstrated_depth == DepthLevel.INTERMEDIATE
