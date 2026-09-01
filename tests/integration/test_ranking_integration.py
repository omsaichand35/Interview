import pytest
from datetime import datetime
import uuid

from interviewos.models import JobProfile
from interviewos.models.skills import SkillRequirement
from interviewos.orchestrator.models import (
    InterviewPlan,
    InterviewRound,
    InterviewRoundType,
    CandidateInterviewContext,
    RoundResult,
    RoundStatus,
    CandidateStatus,
    FinalCandidateStatus
)
from interviewos.orchestrator.engine import InterviewOrchestrator

@pytest.fixture
def mock_job_profile():
    return JobProfile(
        title="Senior Python Engineer",
        required_skills=[SkillRequirement(name="Python"), SkillRequirement(name="SQL")],
        preferred_skills=[SkillRequirement(name="Docker")]
    )

@pytest.fixture
def mock_interview_plan():
    return InterviewPlan(
        role="Senior Python Engineer",
        final_threshold=0.75, # Must get at least 75% overall
        configuration={"shortlist_policy": "hybrid"},
        rounds=[
            InterviewRound(
                name="Technical",
                type=InterviewRoundType.TECHNICAL,
                order=1,
                required=True,
                threshold=0.6,
                configuration={"weight": 1.0}
            ),
            InterviewRound(
                name="HR",
                type=InterviewRoundType.HR,
                order=2,
                required=False,
                threshold=None,
                configuration={"weight": 0.5}
            )
        ]
    )

def test_final_evaluation_and_ranking(mock_job_profile, mock_interview_plan):
    engine = InterviewOrchestrator(llm=None)
    
    # Candidate A: Strong on everything (Shortlisted)
    context_a = CandidateInterviewContext(
        candidate_id="CandA",
        job_id="job",
        interview_plan_id="plan1",
        topics_already_tested=["python", "sql", "docker"],
        round_results={
            mock_interview_plan.rounds[0].round_id: RoundResult(
                round_id=mock_interview_plan.rounds[0].round_id,
                round_type=InterviewRoundType.TECHNICAL,
                score=0.9,
                status=RoundStatus.PASSED,
                strengths=["Great at Python", "Great at Python"], # Should deduplicate
                weaknesses=[],
                competencies={"python": 0.9}
            ),
            mock_interview_plan.rounds[1].round_id: RoundResult(
                round_id=mock_interview_plan.rounds[1].round_id,
                round_type=InterviewRoundType.HR,
                score=0.9,
                status=RoundStatus.COMPLETED,
                strengths=["Great culture fit"],
                weaknesses=[],
                competencies={"communication": 0.9}
            )
        }
    )
    eval_a = engine.build_final_evaluation(mock_interview_plan, context_a, CandidateStatus.COMPLETED, mock_job_profile)
    
    # Candidate B: Fails mandatory technical round (Not Shortlisted)
    context_b = CandidateInterviewContext(
        candidate_id="CandB",
        job_id="job",
        interview_plan_id="plan1",
        topics_already_tested=["python"],
        round_results={
            mock_interview_plan.rounds[0].round_id: RoundResult(
                round_id=mock_interview_plan.rounds[0].round_id,
                round_type=InterviewRoundType.TECHNICAL,
                score=0.5, # Below 0.6 threshold
                status=RoundStatus.FAILED,
                strengths=[],
                weaknesses=["Poor python"],
                competencies={"python": 0.5}
            ),
            mock_interview_plan.rounds[1].round_id: RoundResult(
                round_id=mock_interview_plan.rounds[1].round_id,
                round_type=InterviewRoundType.HR,
                score=1.0,
                status=RoundStatus.COMPLETED,
                strengths=["Perfect fit"],
                weaknesses=[],
                competencies={"communication": 1.0}
            )
        }
    )
    eval_b = engine.build_final_evaluation(mock_interview_plan, context_b, CandidateStatus.COMPLETED, mock_job_profile)

    # Candidate C: Passes all required, but overall weighted score is below 0.75 (Not Shortlisted)
    context_c = CandidateInterviewContext(
        candidate_id="CandC",
        job_id="job",
        interview_plan_id="plan1",
        topics_already_tested=["sql", "python"],
        round_results={
            mock_interview_plan.rounds[0].round_id: RoundResult(
                round_id=mock_interview_plan.rounds[0].round_id,
                round_type=InterviewRoundType.TECHNICAL,
                score=0.65, # Passes 0.6 threshold
                status=RoundStatus.PASSED,
                strengths=[],
                weaknesses=[],
                competencies={"python": 0.65}
            ),
            mock_interview_plan.rounds[1].round_id: RoundResult(
                round_id=mock_interview_plan.rounds[1].round_id,
                round_type=InterviewRoundType.HR,
                score=0.7,
                status=RoundStatus.COMPLETED,
                strengths=[],
                weaknesses=[],
                competencies={"communication": 0.7}
            )
        }
    )
    eval_c = engine.build_final_evaluation(mock_interview_plan, context_c, CandidateStatus.COMPLETED, mock_job_profile)

    # Verify Evaluation A
    assert eval_a.final_status == FinalCandidateStatus.SHORTLISTED
    assert len(eval_a.strengths) == 2 # Deduplicated ("Great at Python", "Great culture fit")
    assert eval_a.strengths[0] == "Great at Python"
    assert eval_a.jd_coverage["Python"] == "TESTED"
    assert eval_a.jd_coverage["SQL"] == "TESTED"
    assert eval_a.jd_coverage["Docker"] == "TESTED"
    
    # Verify Evaluation B
    assert eval_b.final_status == FinalCandidateStatus.NOT_SHORTLISTED
    assert eval_b.jd_coverage["Python"] == "TESTED"
    assert eval_b.jd_coverage["SQL"] == "NOT_TESTED"
    
    # Verify Evaluation C
    assert eval_c.final_status == FinalCandidateStatus.NOT_SHORTLISTED # (0.65 * 1 + 0.7 * 0.5) / 1.5 = (0.65 + 0.35) / 1.5 = 1.0 / 1.5 = 0.66 < 0.75

    from interviewos.orchestrator.ranking import RankingEngine
    
    ranking_engine = RankingEngine()
    ranked = ranking_engine.rank([eval_b, eval_a, eval_c])
    
    # Expected ranking:
    # 1. CandA (Shortlisted)
    # 2. CandC (Not Shortlisted, but score 0.66 is higher than B's score of 0.66? Wait B's score: (0.5*1 + 1.0*0.5) / 1.5 = 1.0/1.5 = 0.66)
    # B and C tie on weighted score, but C completed more? No, both completed 2. C's tech score is 0.65, B's is 0.5. So C > B.
    
    assert ranked[0].candidate_id == "CandA"
    assert ranked[1].candidate_id == "CandC"
    assert ranked[2].candidate_id == "CandB"
