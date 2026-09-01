from interviewos.orchestrator.models import RoundResult
from interviewos.models.learning import LearningGap, LearningPriority

class PerformanceAnalyzer:
    """Analyzes interview round results to extract learning gaps."""

    def __init__(self, target_score: float = 0.8):
        self.target_score = target_score

    def analyze(self, round_results: list[RoundResult]) -> list[LearningGap]:
        """Extract weaknesses and convert them to LearningGaps."""
        gaps = []
        
        for result in round_results:
            if result.status.value in ("skipped", "cancelled"):
                continue
                
            # Iterate through all competencies tested in this round
            for comp_name, score in result.competencies.items():
                if score < self.target_score:
                    # It's a gap.
                    # Determine priority based on round required status or score severity.
                    # We'll base it on score severity.
                    priority = LearningPriority.MEDIUM
                    if score < 0.4:
                        priority = LearningPriority.CRITICAL
                    elif score < 0.6:
                        priority = LearningPriority.HIGH
                        
                    # Filter weaknesses that might belong to this competency.
                    # Since we don't have perfect mapping, we'll assign all round weaknesses 
                    # as evidence if we don't have a better way, but to prevent duplication we 
                    # just pass the weaknesses as evidence for this specific gap.
                    evidence = [w for w in result.weaknesses]
                    
                    gap = LearningGap(
                        competency=comp_name,
                        topic=comp_name.title(),
                        current_score=score,
                        target_score=self.target_score,
                        priority=priority,
                        evidence=evidence,
                        source_round=result.round_type.value,
                        recommended_action=f"Review fundamentals of {comp_name} to improve from {score*100:.0f}% to {self.target_score*100:.0f}%."
                    )
                    gaps.append(gap)
                    
        return gaps
