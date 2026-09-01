import pytest
from interviewos.interview.strategies.dsa import DSAProblemValidator
from interviewos.interview.session import DSAProblem
from interviewos.interview.state import InterviewState, InterviewEvent
from interviewos.interview.state_machine import InterviewStateMachine
from interviewos.interview.session import InterviewSession, InterviewType

def test_dsa_problem_validator():
    validator = DSAProblemValidator()
    
    valid_problem = DSAProblem(
        title="Two Sum",
        statement="Find two numbers that add up to target.",
        difficulty="easy",
        expected_complexity="O(N)",
        hidden_solution_information="Use a hash map.",
        examples=[{"input": "[2,7,11,15], target=9", "output": "[0,1]"}]
    )
    assert validator.validate(valid_problem) == True
    
    invalid_problem = DSAProblem(
        title="No examples",
        statement="Find two numbers.",
        difficulty="easy",
        expected_complexity="O(N)",
        hidden_solution_information="...",
        examples=[]
    )
    assert validator.validate(invalid_problem) == False


def test_state_machine_dsa_transitions():
    machine = InterviewStateMachine()
    session = InterviewSession(id="1", interview_type=InterviewType.DSA, candidate_id="c1", job_id="j1", duration_minutes=30)
    
    machine.transition(session, InterviewEvent.START)
    assert session.state == InterviewState.INTRODUCTION
    
    machine.transition(session, InterviewEvent.PRESENT_PROBLEM)
    assert session.state == InterviewState.PROBLEM_PRESENTATION
    
    machine.transition(session, InterviewEvent.MOVE_TO_UNDERSTANDING)
    assert session.state == InterviewState.UNDERSTANDING
    
    # Test Follow up loops
    machine.transition(session, InterviewEvent.FOLLOW_UP_REQUIRED)
    assert session.state == InterviewState.UNDERSTANDING
    
    machine.transition(session, InterviewEvent.MOVE_TO_APPROACH)
    assert session.state == InterviewState.APPROACH
    
    machine.transition(session, InterviewEvent.FOLLOW_UP_REQUIRED)
    assert session.state == InterviewState.APPROACH
    
    machine.transition(session, InterviewEvent.MOVE_TO_OPTIMIZATION)
    assert session.state == InterviewState.OPTIMIZATION
    
    machine.transition(session, InterviewEvent.FOLLOW_UP_REQUIRED)
    assert session.state == InterviewState.OPTIMIZATION
    
    machine.transition(session, InterviewEvent.NEXT_PROBLEM)
    assert session.state == InterviewState.PROBLEM_PRESENTATION
