import uuid

from interviewos.planning.plan_updater import LearningPlanUpdater
from interviewos.models.learning import LearningGap, LearningPriority
from interviewos.models.plan import PreparationPlan, TopicNode, Priority

def test_plan_updater_existing_topic():
    updater = LearningPlanUpdater()
    
    plan = PreparationPlan(
        goal="Test",
        topics=[
            TopicNode(
                id=uuid.uuid4(),
                title="SQL",
                mastery_score=80.0,
                priority=Priority.MEDIUM
            )
        ]
    )
    
    gap = LearningGap(
        competency="SQL",
        topic="SQL",
        current_score=0.40,
        target_score=0.8,
        priority=LearningPriority.HIGH,
        evidence=["Failed window functions"],
        source_round="technical",
        recommended_action="Review window functions."
    )
    
    updated_plan = updater.update_plan(plan, [gap])
    
    node = updated_plan.topics[0]
    
    # Mastery should be a weighted average. 
    # Current is 80 (implicitly a base score). 
    # With assessment history added, it will recalculate based on the history.
    # Actually, the base score is ignored if history exists (see mastery_engine.py).
    # Since there's 1 assessment (0.4 * 100 = 40.0), mastery should become 40.0.
    
    assert node.mastery_score == 40.0
    assert len(node.assessment_history) == 1
    assert "Failed window functions" in node.assessment_history[0].notes
    assert node.priority == Priority.HIGH

def test_plan_updater_new_topic():
    updater = LearningPlanUpdater()
    
    plan = PreparationPlan(
        goal="Test",
        topics=[]
    )
    
    gap = LearningGap(
        competency="Docker",
        topic="Docker",
        current_score=0.20,
        target_score=0.8,
        priority=LearningPriority.CRITICAL,
        evidence=["No idea what a container is"],
        source_round="project",
        recommended_action="Learn Docker."
    )
    
    updated_plan = updater.update_plan(plan, [gap])
    
    assert len(updated_plan.topics) == 1
    node = updated_plan.topics[0]
    assert node.title == "Docker"
    assert node.mastery_score == 20.0
    assert node.priority == Priority.CRITICAL
