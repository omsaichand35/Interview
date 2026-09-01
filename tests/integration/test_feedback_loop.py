import uuid

from interviewos.models.job import JobProfile
from interviewos.models.plan import PreparationPlan, TopicNode, Priority
from interviewos.orchestrator.models import RoundResult, InterviewRoundType, RoundStatus
from interviewos.analysis.performance_analyzer import PerformanceAnalyzer
from interviewos.planning.plan_updater import LearningPlanUpdater
from interviewos.mentor.learner_state import LearnerStateManager
from interviewos.models.mentor import LearnerState

def test_feedback_loop_end_to_end():
    # 1. Initial Plan exists
    plan = PreparationPlan(
        goal="Senior Python Engineer",
        topics=[
            TopicNode(
                id=uuid.uuid4(),
                title="Python",
                mastery_score=90.0,
                priority=Priority.LOW
            ),
            TopicNode(
                id=uuid.uuid4(),
                title="SQL",
                mastery_score=85.0,
                priority=Priority.MEDIUM
            )
        ]
    )
    
    # 2. Interview happens and produces RoundResults
    tech_round = RoundResult(
        round_id="1",
        round_type=InterviewRoundType.TECHNICAL,
        score=0.7,
        status=RoundStatus.PASSED,
        competencies={"SQL": 0.45, "Python": 0.85},
        weaknesses=["Candidate struggled heavily with SQL window functions."]
    )
    
    # 3. Analyzer extracts weaknesses
    analyzer = PerformanceAnalyzer(target_score=0.8)
    gaps = analyzer.analyze([tech_round])
    
    assert len(gaps) == 1
    assert gaps[0].competency == "SQL"
    
    # 4. Plan Updater applies gaps
    updater = LearningPlanUpdater()
    updated_plan = updater.update_plan(plan, gaps)
    
    sql_node = next(t for t in updated_plan.topics if t.title == "SQL")
    assert sql_node.mastery_score == 45.0 # Since it's the only assessment record, it takes 100% weight
    assert sql_node.priority == Priority.HIGH
    assert len(sql_node.assessment_history) == 1
    assert "Candidate struggled heavily with SQL window functions." in sql_node.assessment_history[0].notes
    
    # Ensure Python remains strong (no gaps reported)
    py_node = next(t for t in updated_plan.topics if t.title == "Python")
    assert py_node.mastery_score == 90.0 # Base score is kept since no assessments added
    
    # 5. Mentor loads context
    state = LearnerState()
    manager = LearnerStateManager(state)
    manager.initialize_from_plan(updated_plan)
    
    sql_progress = next(p for p in state.progress if p.topic == "SQL")
    assert sql_progress.mastery_score == 0.45
    assert sql_progress.priority == "high"
    assert any("window functions" in note for note in sql_progress.notes)
    
    # 6. Verify formatted output looks correct
    formatted = updater.format_plan(updated_plan)
    assert "HIGH PRIORITY" in formatted
    assert "1. SQL" in formatted
    assert "Mastery: 45%" in formatted
    assert "Reason: Interview Performance (technical) weakness" in formatted
