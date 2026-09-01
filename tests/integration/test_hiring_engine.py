import pytest
from unittest.mock import AsyncMock
from interviewos.models import JobProfile
from interviewos.orchestrator.engine import InterviewOrchestrator
from interviewos.orchestrator.models import InterviewPlan, InterviewRound, InterviewRoundType, CandidateStatus, RoundResult, RoundStatus

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_hiring_engine_shortlist(mock_llm_client):
    plan = InterviewPlan(
        role="AI Engineer",
        rounds=[
            InterviewRound(type=InterviewRoundType.OA, name="OA", order=1, threshold=0.6),
            InterviewRound(type=InterviewRoundType.TECHNICAL, name="Tech", order=2, threshold=0.7)
        ]
    )
    
    orchestrator = InterviewOrchestrator(mock_llm_client)
    job = JobProfile(title="AI Engineer")
    
    evaluation = await orchestrator.run_process(plan, "candidate1", job)
    
    assert evaluation.final_status == CandidateStatus.SHORTLISTED
    assert evaluation.rounds_completed == 2
    assert evaluation.round_scores["oa"] == 0.75 # Default simulated score in execute_oa is 0.75
    assert evaluation.round_scores["technical"] == 0.80 # Default simulated score is 0.80

@pytest.mark.asyncio
async def test_hiring_engine_rejection(mock_llm_client, monkeypatch):
    plan = InterviewPlan(
        role="AI Engineer",
        rounds=[
            InterviewRound(type=InterviewRoundType.OA, name="OA", order=1, threshold=0.6),
            InterviewRound(type=InterviewRoundType.TECHNICAL, name="Tech", order=2, threshold=0.9) # This will fail
        ]
    )
    
    orchestrator = InterviewOrchestrator(mock_llm_client)
    job = JobProfile(title="AI Engineer")
    
    evaluation = await orchestrator.run_process(plan, "candidate2", job)
    
    assert evaluation.final_status == CandidateStatus.NOT_SHORTLISTED
    assert evaluation.rounds_completed == 2

@pytest.mark.asyncio
async def test_hiring_engine_disabled_round(mock_llm_client):
    plan = InterviewPlan(
        role="AI Engineer",
        rounds=[
            InterviewRound(type=InterviewRoundType.OA, name="OA", order=1, threshold=0.6),
            InterviewRound(type=InterviewRoundType.TECHNICAL, name="Tech", order=2, threshold=0.7, enabled=False),
            InterviewRound(type=InterviewRoundType.HR, name="HR", order=3, threshold=0.6)
        ]
    )
    
    orchestrator = InterviewOrchestrator(mock_llm_client)
    job = JobProfile(title="AI Engineer")
    
    evaluation = await orchestrator.run_process(plan, "candidate3", job)
    
    assert evaluation.final_status == CandidateStatus.SHORTLISTED
    assert evaluation.rounds_completed == 2 # OA and HR only
    assert "technical" not in evaluation.round_scores
