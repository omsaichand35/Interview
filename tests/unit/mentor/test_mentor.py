from interviewos.mentor import LearnerStateManager
from interviewos.models.plan import PreparationPlan, TopicNode, Priority


def test_learner_state_initialization() -> None:
    plan = PreparationPlan(
        goal="AI Engineer",
        topics=[
            TopicNode(
                title="Python",
                mastery_score=0.0,
                priority=Priority.HIGH,
            )
        ],
    )

    manager = LearnerStateManager()

    manager.initialize_from_plan(plan)

    state = manager.get_state()

    assert state.target_role == "AI Engineer"
    assert len(state.progress) == 1
    assert state.progress[0].topic == "Python"