from typing import Literal

from interviewos.orchestrator.models import FinalInterviewEvaluation, FinalCandidateStatus

class RankingEngine:
    """Ranks candidates deterministically based on final evaluations."""
    
    def __init__(self, policy: Literal["top_n", "minimum_score", "top_percentage", "threshold_only"] = "threshold_only", value: float | None = None):
        self.policy = policy
        self.value = value

    def rank(self, evaluations: list[FinalInterviewEvaluation]) -> list[FinalInterviewEvaluation]:
        # Sort criteria: 
        # 1. Status (SHORTLISTED first)
        # 2. Weighted score
        # 3. Number of rounds completed
        
        def sort_key(eval_obj: FinalInterviewEvaluation):
            is_shortlisted = eval_obj.final_status == FinalCandidateStatus.SHORTLISTED
            score = eval_obj.weighted_score if eval_obj.weighted_score is not None else 0.0
            technical_score = eval_obj.round_scores.get("technical", 0.0)
            return (
                1 if is_shortlisted else 0,
                score,
                eval_obj.rounds_completed,
                technical_score
            )
            
        sorted_evals = sorted(evaluations, key=sort_key, reverse=True)
        
        if self.policy == "top_n" and self.value is not None:
            return sorted_evals[:int(self.value)]
        elif self.policy == "top_percentage" and self.value is not None:
            cutoff = max(1, int(len(sorted_evals) * self.value))
            return sorted_evals[:cutoff]
        elif self.policy == "minimum_score" and self.value is not None:
            return [e for e in sorted_evals if e.weighted_score is not None and e.weighted_score >= self.value]
            
        # threshold_only (default)
        return sorted_evals
