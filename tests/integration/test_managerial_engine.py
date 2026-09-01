import pytest
from unittest.mock import AsyncMock
import uuid

from interviewos.interview.engine import InterviewEngine
from interviewos.interview.session import InterviewSession, InterviewType, InterviewState
from interviewos.interview.state_machine import InterviewStateMachine
from interviewos.interview.brain import InterviewBrain
from interviewos.interview.interviewer import Interviewer
from interviewos.interview.strategies.managerial import ManagerialInterviewStrategy
from interviewos.interview.context_builder import InterviewContextBuilder
from interviewos.models import JobProfile

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    
    async def generate_mock(prompt, system_prompt):
        if "I aligned engineering metrics" in prompt:
            # Strong answer -> Deep Dive or Move On
            return '''{
                "assessment": {
                    "score": 0.9,
                    "strengths": ["Excellent strategic alignment"],
                    "weaknesses": [],
                    "managerial_strategic_thinking_score": 0.9,
                    "managerial_evidence": [
                        {
                            "observed_action": "Aligned engineering metrics with business OKRs",
                            "inferred_competency": "Strategic Thinking"
                        }
                    ],
                    "demonstrated_depth": "expert"
                },
                "action": "move_on",
                "next_competency": "Conflict Management",
                "next_question": "Tell me about a time you had a conflict with a stakeholder.",
                "difficulty_change": "increase",
                "reasoning": "Candidate demonstrated strong strategic thinking."
            }'''
        else:
            # Weak vague answer -> Follow up
            return '''{
                "assessment": {
                    "score": 0.4,
                    "strengths": [],
                    "weaknesses": ["Vague answer, lacks concrete details on the decision making process"],
                    "managerial_delegation_score": 0.4,
                    "managerial_evidence": [
                        {
                            "observed_action": "Gave task to John",
                            "inferred_competency": "Basic delegation without framework"
                        }
                    ],
                    "managerial_concerns": ["Candidate didn't explain the why"],
                    "demonstrated_depth": "foundational"
                },
                "action": "ask_follow_up",
                "next_competency": "Delegation",
                "next_question": "How did you decide John was the right person?",
                "difficulty_change": "same",
                "reasoning": "Candidate answer was too vague."
            }'''
            
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        json_str = await generate_mock(prompt, system_prompt)
        return model(**json.loads(json_str))
    client.generate_structured.side_effect = _generate_structured_wrapper
    return client

@pytest.mark.asyncio
async def test_managerial_engine_flow(mock_llm_client):
    job = JobProfile(title="Engineering Manager")
    session = InterviewSession(
        id=str(uuid.uuid4()),
        interview_type=InterviewType.MANAGERIAL,
        candidate_id="cand1",
        job_id="job1",
        duration_minutes=30
    )
    
    engine = InterviewEngine(
        interviewer=Interviewer(mock_llm_client),
        state_machine=InterviewStateMachine(),
        brain=InterviewBrain(mock_llm_client, Interviewer(mock_llm_client), ManagerialInterviewStrategy())
    )
    
    engine.start(session)
    engine.introduce(session, "Welcome.")
    engine.ask(session, "Tell me about a time you delegated a task.")
    
    assert session.state == InterviewState.QUESTIONING
    
    # 1. Provide a vague answer
    context = InterviewContextBuilder().build(job, session)
    decision = await engine.process_answer(context, "I gave the task to John.")
    
    assert session.state == InterviewState.FOLLOW_UP
    assert session.current_question == "How did you decide John was the right person?"
    assert decision.assessment.managerial_delegation_score == 0.4
    
    # 2. Provide a strong answer
    engine.ask(session, "How do you align tech with business?")
    context = InterviewContextBuilder().build(job, session)
    decision = await engine.process_answer(context, "I aligned engineering metrics with business OKRs.")
    
    assert session.state == InterviewState.QUESTIONING
    assert decision.assessment.managerial_strategic_thinking_score == 0.9
