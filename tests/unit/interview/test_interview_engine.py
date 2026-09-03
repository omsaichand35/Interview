import pytest
from unittest.mock import MagicMock

from interviewos.interview.engine import InterviewEngine
from interviewos.interview.session import InterviewSession, InterviewType, InterviewScore, AnswerAssessment, InterviewDecision, DifficultyChange
from interviewos.interview.state import InterviewState, InterviewAction


def test_apply_decision_populates_strengths_and_weaknesses():
    interviewer = MagicMock()
    state_machine = MagicMock()
    brain = MagicMock()

    engine = InterviewEngine(interviewer, state_machine, brain)
    session = InterviewSession(id="s1", interview_type=InterviewType.TECHNICAL, candidate_id="c1", job_id="j1", duration_minutes=20)

    assessment = AnswerAssessment(
        score=0.85,
        strengths=["Clear explanation of API bounds", "Good grasp of complexity"],
        weaknesses=["Missed edge case for empty input"],
        feedback="Overall solid answer."
    )

    decision = InterviewDecision(
        action=InterviewAction.MOVE_ON,
        assessment=assessment,
        next_competency="System Design",
        difficulty_change=DifficultyChange.SAME,
    )

    engine._apply_decision(session, decision)

    assert len(session.scores) == 1
    score = session.scores[0]
    assert score.score == 0.85
    assert score.strengths == ["Clear explanation of API bounds", "Good grasp of complexity"]
    assert score.weaknesses == ["Missed edge case for empty input"]
    assert score.feedback == "Overall solid answer."
