from datetime import datetime
from uuid import UUID

from interviewos.models.plan import AssessmentRecord, PreparationPlan
from interviewos.storage.plan_repository import PlanRepository

from .mastery_engine import MasteryEngine
from .priority_engine import PriorityEngine
from .recommendation_engine import RecommendationEngine


class PlanManager:
    """Orchestrates updates to the PreparationPlan."""

    def __init__(
        self,
        repository: PlanRepository,
        mastery_engine: MasteryEngine | None = None,
        priority_engine: PriorityEngine | None = None,
        recommendation_engine: RecommendationEngine | None = None,
    ) -> None:
        self.repository = repository
        self.mastery_engine = mastery_engine or MasteryEngine()
        self.priority_engine = priority_engine or PriorityEngine()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    def record_assessment(
        self,
        plan_id: UUID,
        topic_id: UUID,
        score: float,
        context: str | None = None,
        notes: str | None = None,
    ) -> PreparationPlan:
        """Record an assessment score for a topic and recalculate the plan."""
        plan = self.repository.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found.")

        all_nodes = plan.get_all_nodes()
        topic = all_nodes.get(topic_id)
        if not topic:
            raise ValueError(f"Topic {topic_id} not found in plan {plan_id}.")

        # 1. Add assessment record
        record = AssessmentRecord(
            score=score,
            context=context,
            notes=notes,
        )
        topic.assessment_history.append(record)

        # 2. Recalculate Mastery for the whole tree (which updates state)
        self.mastery_engine.recalculate_plan(plan)

        # 3. Recalculate Priorities based on new mastery
        self.priority_engine.update_priorities(plan)

        # 4. Generate next recommendation
        recommended_node, reason = self.recommendation_engine.get_recommendation(plan)
        if recommended_node:
            plan.recommended_next_topic_id = recommended_node.id

        # 5. Save changes
        plan.last_updated = datetime.now()
        self.repository.save(plan)

        return plan

    def save_plan(self, plan: PreparationPlan) -> None:
        """Save a new or explicitly modified plan."""
        # Ensure it's up to date before saving
        self.mastery_engine.recalculate_plan(plan)
        self.priority_engine.update_priorities(plan)
        
        recommended_node, reason = self.recommendation_engine.get_recommendation(plan)
        if recommended_node:
            plan.recommended_next_topic_id = recommended_node.id
            
        plan.last_updated = datetime.now()
        self.repository.save(plan)
