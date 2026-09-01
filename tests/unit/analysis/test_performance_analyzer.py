import pytest
from interviewos.orchestrator.models import RoundResult, InterviewRoundType, RoundStatus
from interviewos.analysis.performance_analyzer import PerformanceAnalyzer
from interviewos.models.learning import LearningPriority

def test_performance_analyzer_extracts_gaps():
    analyzer = PerformanceAnalyzer(target_score=0.8)
    
    # 1. Round result with low score
    res1 = RoundResult(
        round_id="1",
        round_type=InterviewRoundType.TECHNICAL,
        score=0.45,
        status=RoundStatus.COMPLETED,
        competencies={"SQL": 0.45, "Python": 0.85},
        weaknesses=["Failed to optimize window functions"]
    )
    
    # 2. Round result skipped
    res2 = RoundResult(
        round_id="2",
        round_type=InterviewRoundType.HR,
        score=0.0,
        status=RoundStatus.SKIPPED,
        competencies={"Communication": 0.0}
    )
    
    gaps = analyzer.analyze([res1, res2])
    
    # Python is 0.85 (>=0.8), so it's not a gap.
    # HR is skipped, so it shouldn't be analyzed.
    # SQL is 0.45, so it's a gap.
    
    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.competency == "SQL"
    assert gap.topic == "Sql"
    assert gap.current_score == 0.45
    assert gap.target_score == 0.8
    assert gap.priority == LearningPriority.HIGH # 0.45 is between 0.4 and 0.6
    assert gap.source_round == "technical"
    assert "Failed to optimize window functions" in gap.evidence
