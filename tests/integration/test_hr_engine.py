import pytest
from unittest.mock import AsyncMock
from interviewos.interview.engine import InterviewEngine
from interviewos.interview.session import InterviewSession, InterviewType, InterviewDecision, AnswerAssessment, DifficultyChange, HREvidence, DepthLevel
from interviewos.interview.state import InterviewState, InterviewEvent, InterviewAction
from interviewos.interview.state_machine import InterviewStateMachine
from interviewos.interview.brain import InterviewBrain
from interviewos.interview.interviewer import Interviewer
from interviewos.interview.strategies.hr import HRInterviewStrategy
from interviewos.interview.context_builder import InterviewContextBuilder
from interviewos.models import JobProfile

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    
    async def generate_mock(prompt, system_prompt):
        if "Determine what should happen next" in prompt:
            if "I actually asked them to explain their perspective" in prompt:
                # Strong answer
                return '''{
                    "assessment": {
                        "score": 0.9,
                        "strengths": ["Clear communication, strong ownership"],
                        "hr_relevance_score": 1.0,
                        "hr_ownership_score": 1.0,
                        "hr_evidence": [
                            {
                                "situation": "Disagreed on architecture",
                                "task": "Resolve conflict",
                                "action": "I asked them to explain",
                                "result": "Combined approaches"
                            }
                        ],
                        "demonstrated_depth": "intermediate"
                    },
                    "action": "move_on",
                    "next_competency": "Motivation",
                    "next_question": "Why do you want to work here?",
                    "difficulty_change": "increase",
                    "reasoning": "Candidate demonstrated strong teamwork and conflict resolution."
                }'''
            elif "we had some issues" in prompt:
                # Weak vague answer -> Follow up
                return '''{
                    "assessment": {
                        "score": 0.4,
                        "strengths": [],
                        "weaknesses": ["Vague answer, lacks concrete details"],
                        "hr_relevance_score": 0.5,
                        "hr_evidence": [
                            {
                                "situation": "Had some issues",
                                "result": "Solved them"
                            }
                        ],
                        "hr_concerns": ["Candidate used 'we' instead of 'I'"],
                        "demonstrated_depth": "foundational"
                    },
                    "action": "ask_follow_up",
                    "next_competency": "Teamwork",
                    "next_question": "What exactly were the issues and what did you personally do?",
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
async def test_hr_interview_integration(mock_llm_client):
    job = JobProfile(title="AI Engineer")
    strategy = HRInterviewStrategy()
    
    session = InterviewSession(id="hr1", interview_type=InterviewType.HR, candidate_id="c1", job_id="j1", duration_minutes=30)
    engine = InterviewEngine(
        interviewer=Interviewer(mock_llm_client),
        state_machine=InterviewStateMachine(),
        brain=InterviewBrain(mock_llm_client, Interviewer(mock_llm_client), strategy)
    )
    
    engine.start(session)
    engine.introduce(session, "Welcome.")
    
    engine.ask(session, "Tell me about a disagreement you had with a teammate.")
    
    context = InterviewContextBuilder().build(job=job, session=session)
    
    # Vague answer
    decision = await engine.process_answer(context, "we had some issues but eventually solved them.")
    
    assert session.state == InterviewState.FOLLOW_UP
    assert decision.assessment.hr_concerns[0] == "Candidate used 'we' instead of 'I'"
    assert decision.next_question == "What exactly were the issues and what did you personally do?"
    
    # Strong answer to follow up
    decision2 = await engine.process_answer(context, "I actually asked them to explain their perspective, and I proposed a compromise.")
    
    assert session.state == InterviewState.QUESTIONING
    assert decision2.assessment.hr_ownership_score == 1.0
    assert decision2.difficulty_change == DifficultyChange.INCREASE
