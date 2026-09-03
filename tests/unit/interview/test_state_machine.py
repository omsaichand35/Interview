import pytest

from interviewos.interview.session import InterviewSession, InterviewType
from interviewos.interview.state import InterviewState, InterviewEvent
from interviewos.interview.state_machine import InterviewStateMachine


def test_state_machine_introduction_complete():
    sm = InterviewStateMachine()
    session = InterviewSession(id="s1", interview_type=InterviewType.TECHNICAL, candidate_id="c1", job_id="j1", duration_minutes=20)
    assert session.state == InterviewState.CREATED

    sm.transition(session, InterviewEvent.START)
    assert session.state == InterviewState.INTRODUCTION

    sm.transition(session, InterviewEvent.INTRODUCTION_COMPLETE)
    assert session.state == InterviewState.QUESTIONING


def test_state_machine_answer_received_from_introduction():
    sm = InterviewStateMachine()
    session = InterviewSession(id="s2", interview_type=InterviewType.PROJECT, candidate_id="c1", job_id="j1", duration_minutes=20)

    sm.transition(session, InterviewEvent.START)
    assert session.state == InterviewState.INTRODUCTION

    # Receiving an answer directly from introduction should safely transition to QUESTIONING
    sm.transition(session, InterviewEvent.ANSWER_RECEIVED)
    assert session.state == InterviewState.QUESTIONING
