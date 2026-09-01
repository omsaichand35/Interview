import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
import uuid

from interviewos.models import JobProfile
from interviewos.orchestrator.engine import InterviewOrchestrator
from interviewos.orchestrator.models import (
    InterviewPlan, 
    InterviewRound, 
    InterviewRoundType, 
    ShortlistPolicy,
    FinalCandidateStatus,
    RoundStatus
)
from interviewos.core.exceptions import LLMUnavailableError

@pytest.fixture
def mock_llm():
    return AsyncMock()

@pytest.mark.asyncio
async def test_orchestrator_handles_round_failure(mock_llm):
    """
    Test that the orchestrator degrades gracefully when execute_round raises
    an LLMUnavailableError during a mandatory round.
    It should mark the round as FAILED and terminate early if stop_on_failure is True.
    """
    orchestrator = InterviewOrchestrator(mock_llm)
    
    plan = InterviewPlan(
        plan_id="plan1",
        name="Backend Engineering Plan",
        role="Backend Engineer",
        job_id="job1",
        rounds=[
            InterviewRound(
                round_id="r1",
                name="System Design",
                type=InterviewRoundType.TECHNICAL,
                order=1,
                required=True,
                threshold=0.6,
                configuration={"stop_on_failure": True}
            ),
            InterviewRound(
                round_id="r2",
                name="Behavioral",
                type=InterviewRoundType.HR,
                order=2,
                required=True,
                threshold=0.5
            )
        ],
        configuration={"shortlist_policy": ShortlistPolicy.ALL_REQUIRED_ROUNDS_PASS}
    )
    
    job = JobProfile(title="Backend Engineer")
    
    # Patch execute_round to raise LLMUnavailableError on the first call
    call_count = 0
    async def failing_execute_round(round_config, context, job):
        nonlocal call_count
        call_count += 1
        raise LLMUnavailableError("API timed out")
    
    with patch.object(orchestrator, "execute_round", side_effect=failing_execute_round):
        final_evaluation = await orchestrator.run_process(
            plan=plan, 
            candidate_id="cand1", 
            job=job
        )
    
    # 1. The first round should score 0.0 because execute_round raised an error
    assert final_evaluation.round_scores.get("technical") == 0.0
    
    # 2. The second round should not have been executed (stop_on_failure=True)
    assert "hr" not in final_evaluation.round_scores
    
    # 3. Final status must be NOT_SHORTLISTED
    assert final_evaluation.final_status == FinalCandidateStatus.NOT_SHORTLISTED
    
    # 4. execute_round should have been called exactly once (it failed on round 1)
    assert call_count == 1

