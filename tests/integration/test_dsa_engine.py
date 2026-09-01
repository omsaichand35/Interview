import pytest
from unittest.mock import Mock, AsyncMock
from interviewos.interview.engine import InterviewEngine
from interviewos.interview.session import InterviewSession, InterviewType, InterviewDecision, AnswerAssessment
from interviewos.interview.state import InterviewState, InterviewEvent, InterviewAction
from interviewos.interview.state_machine import InterviewStateMachine
from interviewos.interview.brain import InterviewBrain
from interviewos.interview.interviewer import Interviewer
from interviewos.interview.strategies.dsa import DSAInterviewStrategy, DSAProblemGenerator
from interviewos.interview.context_builder import InterviewContextBuilder
from interviewos.models import JobProfile

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    
    # We will simulate the LLM responding to generating a problem and evaluating answers
    async def generate_mock(prompt, system_prompt):
        if "Generate a Data Structures" in prompt:
            return '''{
                "title": "Contains Duplicate",
                "statement": "Given an integer array nums, return true if any value appears at least twice.",
                "difficulty": "easy",
                "topics": ["Array", "Hash Table"],
                "constraints": ["1 <= nums.length <= 10^5"],
                "examples": [{"input": "nums = [1,2,3,1]", "output": "true"}],
                "expected_complexity": "O(N) time, O(N) space",
                "hidden_solution_information": "Use a hash set to track seen elements."
            }'''
            
        if "Determine what should happen next." in prompt:
            # We determine where we are by the transcript or action
            if "I would use a set and scan the array once" in prompt:
                # Evaluating approach - candidate gave O(n) hash set
                return '''{
                    "assessment": {
                        "score": 0.9,
                        "strengths": ["Optimal O(n) solution using hash set."],
                        "algorithmic_reasoning_score": 0.9,
                        "complexity_score": 0.9
                    },
                    "action": "move_on",
                    "next_competency": "optimization",
                    "difficulty_change": "same",
                    "next_question": "Excellent. Can you do it in O(1) space?"
                }'''
            else:
                # Understanding phase
                return '''{
                    "assessment": {
                        "score": 0.8,
                        "strengths": ["Understood the core goal."],
                        "problem_understanding_score": 0.8
                    },
                    "action": "move_on",
                    "next_competency": "approach",
                    "difficulty_change": "same",
                    "next_question": "How would you approach this problem?"
                }'''
            
    async def _generate_structured_wrapper(prompt, model, system_prompt=None, **kwargs):
        import json
        json_str = await generate_mock(prompt, system_prompt)
        return model(**json.loads(json_str))
    client.generate_structured.side_effect = _generate_structured_wrapper
    
    # Mock sync_generate for components that might use it (none here ideally)
    def sync_generate_mock(prompt, system_prompt):
        import asyncio
        return asyncio.run(generate_mock(prompt, system_prompt))
    client.sync_generate.side_effect = sync_generate_mock
    
    return client

@pytest.mark.asyncio
async def test_dsa_interview_integration(mock_llm_client):
    job = JobProfile(title="AI Engineer", summary="AI things", required_skills=[])
    strategy = DSAInterviewStrategy()
    
    session = InterviewSession(id="1", interview_type=InterviewType.DSA, candidate_id="c1", job_id="j1", duration_minutes=30)
    engine = InterviewEngine(
        interviewer=Interviewer(mock_llm_client),
        state_machine=InterviewStateMachine(),
        brain=InterviewBrain(mock_llm_client, Interviewer(mock_llm_client), strategy)
    )
    
    engine.start(session)
    engine.introduce(session, "Welcome.")
    
    # Generate problem
    generator = DSAProblemGenerator(mock_llm_client)
    problem = await generator.generate(job, "easy", [])
    assert problem.title == "Contains Duplicate"
    session.current_dsa_problem = problem
    session.dsa_problems.append(problem)
    
    engine.state_machine.transition(session, InterviewEvent.PRESENT_PROBLEM)
    engine.state_machine.transition(session, InterviewEvent.MOVE_TO_UNDERSTANDING)
    engine.ask(session, "Explain your understanding.")
    
    assert session.state == InterviewState.UNDERSTANDING
    
    context = InterviewContextBuilder().build(job=job, session=session)
    
    # Candidate understanding
    decision = await engine.process_answer(context, "The goal is to determine whether any value occurs more than once.")
    
    # Decision was MOVE_ON during UNDERSTANDING -> engine should transition to APPROACH
    assert session.state == InterviewState.APPROACH
    assert decision.assessment.problem_understanding_score == 0.8
    
    # Candidate approach
    decision2 = await engine.process_answer(context, "I would use a set and scan the array once. Return true if exists.")
    
    # Decision was MOVE_ON during APPROACH -> engine should transition to OPTIMIZATION
    assert session.state == InterviewState.OPTIMIZATION
    assert decision2.assessment.algorithmic_reasoning_score == 0.9
    
    # Check transcript
    transcript = [msg.content for msg in session.transcript]
    assert "Explain your understanding." in transcript
    assert "The goal is to determine whether any value occurs more than once." in transcript
    assert "I would use a set and scan the array once. Return true if exists." in transcript
