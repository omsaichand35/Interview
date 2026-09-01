import pytest

from interviewos.orchestrator.models import FinalInterviewEvaluation, FinalCandidateStatus
from interviewos.orchestrator.ranking import RankingEngine

def test_ranking_sort_order():
    eval1 = FinalInterviewEvaluation(
        candidate_id="cand1",
        role="Engineer",
        rounds_completed=4,
        round_scores={"technical": 0.8},
        weighted_score=0.85,
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )
    
    eval2 = FinalInterviewEvaluation(
        candidate_id="cand2",
        role="Engineer",
        rounds_completed=4,
        round_scores={"technical": 0.9},
        weighted_score=0.90,
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )
    
    eval3 = FinalInterviewEvaluation(
        candidate_id="cand3",
        role="Engineer",
        rounds_completed=4,
        round_scores={"technical": 0.7},
        weighted_score=0.88,
        final_status=FinalCandidateStatus.NOT_SHORTLISTED,
        recommendation="Reject"
    )
    
    # Tie case
    eval4 = FinalInterviewEvaluation(
        candidate_id="cand4",
        role="Engineer",
        rounds_completed=4,
        round_scores={"technical": 0.95},
        weighted_score=0.85, # Tie with cand1 on weighted_score
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )

    evals = [eval1, eval2, eval3, eval4]
    
    engine = RankingEngine(policy="threshold_only")
    ranked = engine.rank(evals)
    
    # Expected order:
    # 1. cand2 (SHORTLISTED, 0.90)
    # 2. cand4 (SHORTLISTED, 0.85, higher tech score 0.95 vs 0.8)
    # 3. cand1 (SHORTLISTED, 0.85, lower tech score)
    # 4. cand3 (NOT_SHORTLISTED, 0.88 - status takes precedence)
    
    assert ranked[0].candidate_id == "cand2"
    assert ranked[1].candidate_id == "cand4"
    assert ranked[2].candidate_id == "cand1"
    assert ranked[3].candidate_id == "cand3"

def test_ranking_top_n():
    eval1 = FinalInterviewEvaluation(
        candidate_id="cand1",
        role="Engineer",
        rounds_completed=4,
        round_scores={},
        weighted_score=0.85,
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )
    eval2 = FinalInterviewEvaluation(
        candidate_id="cand2",
        role="Engineer",
        rounds_completed=4,
        round_scores={},
        weighted_score=0.95,
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )
    
    engine = RankingEngine(policy="top_n", value=1)
    ranked = engine.rank([eval1, eval2])
    
    assert len(ranked) == 1
    assert ranked[0].candidate_id == "cand2"

def test_ranking_minimum_score():
    eval1 = FinalInterviewEvaluation(
        candidate_id="cand1",
        role="Engineer",
        rounds_completed=4,
        round_scores={},
        weighted_score=0.75,
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )
    eval2 = FinalInterviewEvaluation(
        candidate_id="cand2",
        role="Engineer",
        rounds_completed=4,
        round_scores={},
        weighted_score=0.90,
        final_status=FinalCandidateStatus.SHORTLISTED,
        recommendation="Proceed"
    )
    
    engine = RankingEngine(policy="minimum_score", value=0.80)
    ranked = engine.rank([eval1, eval2])
    
    assert len(ranked) == 1
    assert ranked[0].candidate_id == "cand2"
