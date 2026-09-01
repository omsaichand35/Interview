import pytest
from interviewos.orchestrator.models import InterviewPlan, InterviewRound, InterviewRoundType, ShortlistPolicy
from interviewos.orchestrator.plan import PlanValidator
from pydantic import ValidationError

def test_plan_validation_valid():
    plan = InterviewPlan(
        role="AI Engineer",
        rounds=[
            InterviewRound(type=InterviewRoundType.OA, name="OA", order=1, threshold=0.6),
            InterviewRound(type=InterviewRoundType.TECHNICAL, name="Tech", order=2, threshold=0.7)
        ]
    )
    # Should not raise
    PlanValidator.validate(plan)

def test_plan_validation_duplicate_rounds():
    plan = InterviewPlan(
        role="AI Engineer",
        rounds=[
            InterviewRound(type=InterviewRoundType.OA, name="OA", order=1),
            InterviewRound(type=InterviewRoundType.OA, name="OA2", order=2)
        ]
    )
    with pytest.raises(ValueError, match="Duplicate round type"):
        PlanValidator.validate(plan)

def test_plan_validation_invalid_threshold():
    # Pydantic catches this during instantiation
    with pytest.raises(ValidationError):
        plan = InterviewPlan(
            role="AI Engineer",
            rounds=[
                InterviewRound(type=InterviewRoundType.OA, name="OA", order=1, threshold=1.5)
            ]
        )
