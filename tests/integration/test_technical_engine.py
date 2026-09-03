import pytest
from unittest.mock import AsyncMock
from interviewos.interview.engine import InterviewEngine
from interviewos.interview.session import (
    InterviewSession,
    InterviewType,
    InterviewDecision,
    AnswerAssessment,
    DifficultyChange,
    Misconception,
    DepthLevel,
)
from interviewos.interview.state import InterviewState, InterviewEvent, InterviewAction
from interviewos.interview.state_machine import InterviewStateMachine
from interviewos.interview.brain import InterviewBrain
from interviewos.interview.interviewer import Interviewer
from interviewos.interview.strategies.technical import TechnicalInterviewStrategy
from interviewos.interview.context_builder import InterviewContextBuilder
from interviewos.models import JobProfile


@pytest.fixture
def mock_llm_client():
    client = AsyncMock()

    async def generate_mock(prompt, system_prompt):
        assert "model_json_schema" not in prompt
        assert '"assessment"' in prompt
        if "Determine what should happen next" in prompt:
            if "Oh right, backward() computes gradients" in prompt:
                # Strong answer
                return """{
                    "assessment": {
                        "score": 0.9,
                        "strengths": ["Clear understanding"],
                        "technical_correctness_score": 1.0,
                        "demonstrated_depth": "intermediate"
                    },
                    "action": "move_on",
                    "next_competency": "Machine Learning",
                    "next_question": "Let's talk about overfitting.",
                    "difficulty_change": "increase",
                    "reasoning": "Candidate did well."
                }"""
            elif "loss.backward() updates weights" in prompt:
                # Weak answer with misconception -> Follow up
                return """{
                    "assessment": {
                        "score": 0.4,
                        "strengths": [],
                        "weaknesses": ["Thinks backward updates weights"],
                        "technical_correctness_score": 0.3,
                        "misconceptions": [
                            {
                                "concept": "Backprop",
                                "misconception": "backward() updates weights",
                                "correction": "backward() computes gradients, step() updates weights"
                            }
                        ],
                        "demonstrated_depth": "foundational"
                    },
                    "action": "ask_follow_up",
                    "next_competency": "PyTorch",
                    "next_question": "What is the role of optimizer.step()?",
                    "difficulty_change": "same",
                    "reasoning": "Candidate has a misconception, asking a clarifying follow-up."
                }"""
            else:
                # Strong answer
                return """{
                    "assessment": {
                        "score": 0.9,
                        "strengths": ["Clear understanding"],
                        "technical_correctness_score": 1.0,
                        "demonstrated_depth": "intermediate"
                    },
                    "action": "move_on",
                    "next_competency": "Machine Learning",
                    "next_question": "Let's talk about overfitting.",
                    "difficulty_change": "increase",
                    "reasoning": "Candidate did well."
                }"""

    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json

        json_str = await generate_mock(prompt, system_prompt)
        return model(**json.loads(json_str))

    client.generate_structured.side_effect = _generate_structured_wrapper
    return client


@pytest.mark.asyncio
async def test_technical_interview_integration(mock_llm_client):
    job = JobProfile(title="AI Engineer")
    strategy = TechnicalInterviewStrategy()

    session = InterviewSession(
        id="tech1",
        interview_type=InterviewType.TECHNICAL,
        candidate_id="c1",
        job_id="j1",
        duration_minutes=30,
    )
    engine = InterviewEngine(
        interviewer=Interviewer(mock_llm_client),
        state_machine=InterviewStateMachine(),
        brain=InterviewBrain(mock_llm_client, Interviewer(mock_llm_client), strategy),
    )

    engine.start(session)
    engine.introduce(session, "Welcome.")

    # Simulate a generated question
    engine.ask(session, "What happens when loss.backward() is called?")

    context = InterviewContextBuilder().build(job=job, session=session)

    # Bad answer
    decision = await engine.process_answer(context, "loss.backward() updates weights.")

    assert session.state == InterviewState.FOLLOW_UP
    assert decision.assessment.misconceptions[0].concept == "Backprop"
    assert decision.assessment.demonstrated_depth == DepthLevel.FOUNDATIONAL
    assert decision.next_question == "What is the role of optimizer.step()?"

    # Good answer to follow up
    decision2 = await engine.process_answer(
        context, "Oh right, backward() computes gradients, step() updates weights."
    )

    assert session.state == InterviewState.QUESTIONING
    assert decision2.assessment.demonstrated_depth == DepthLevel.INTERMEDIATE
    assert decision2.difficulty_change == DifficultyChange.INCREASE
