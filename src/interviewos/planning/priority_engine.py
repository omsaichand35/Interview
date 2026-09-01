from interviewos.models.plan import PreparationPlan, Priority, TopicNode


class PriorityEngine:
    """Adjusts topic priorities dynamically based on mastery and gaps."""

    def update_priorities(self, plan: PreparationPlan) -> None:
        """Update priorities for all topics in the plan."""
        for topic in plan.topics:
            self._update_topic_priority(topic)

    def _update_topic_priority(self, topic: TopicNode) -> None:
        """
        Dynamically calculate priority based on mastery score.
        If a topic is completely unmastered or needs review, its priority increases.
        If it is mastered, its priority drops.
        """
        # First process children
        for child in topic.subtopics:
            self._update_topic_priority(child)

        # Basic priority recalculation logic based on mastery
        if topic.mastery_score >= 85.0:
            topic.priority = Priority.LOW
        elif topic.mastery_score >= 60.0:
            topic.priority = Priority.MEDIUM
        elif topic.mastery_score >= 30.0:
            topic.priority = Priority.HIGH
        else:
            topic.priority = Priority.CRITICAL
