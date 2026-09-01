from interviewos.models.plan import PreparationPlan, TopicNode, TopicState


class MasteryEngine:
    """Calculates and updates mastery scores for a dynamic preparation plan."""

    def recalculate_plan(self, plan: PreparationPlan) -> None:
        """Recalculate mastery scores for the entire plan tree."""
        total_mastery = 0.0
        count = 0
        
        for topic in plan.topics:
            self.recalculate_topic(topic)
            total_mastery += topic.mastery_score
            count += 1
            
        if count > 0:
            plan.overall_mastery = round(total_mastery / count, 2)
        else:
            plan.overall_mastery = 0.0

    def recalculate_topic(self, topic: TopicNode) -> float:
        """
        Recursively recalculate mastery for a topic and its subtopics.
        
        If a topic has subtopics, its mastery is the average of its subtopics.
        If a topic is a leaf node, its mastery is derived from its assessment history.
        """
        if topic.subtopics:
            total_mastery = 0.0
            for subtopic in topic.subtopics:
                total_mastery += self.recalculate_topic(subtopic)
                
            topic.mastery_score = round(total_mastery / len(topic.subtopics), 2)
        else:
            # Leaf node calculation based on assessment history
            if not topic.assessment_history:
                # If no assessments, mastery remains whatever its base/initial value is
                pass
            else:
                # Use a weighted average of the last 3 assessments, favoring the most recent
                recent = sorted(
                    topic.assessment_history, 
                    key=lambda a: a.timestamp, 
                    reverse=True
                )[:3]
                
                weights = [0.6, 0.3, 0.1]
                weighted_sum = 0.0
                weight_total = 0.0
                
                for i, assessment in enumerate(recent):
                    weight = weights[i]
                    weighted_sum += assessment.score * weight
                    weight_total += weight
                    
                topic.mastery_score = round(weighted_sum / weight_total, 2)

        # Update topic state based on mastery if not manually overridden
        # E.g., if mastery > 90, it might be MASTERED.
        # This can be refined, but simple threshold logic helps.
        if topic.mastery_score >= 90.0:
            topic.state = TopicState.MASTERED
        elif topic.mastery_score < 40.0 and topic.state != TopicState.NOT_STARTED:
            topic.state = TopicState.NEEDS_REVIEW

        return topic.mastery_score
