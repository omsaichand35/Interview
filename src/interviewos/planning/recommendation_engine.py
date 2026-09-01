from typing import Tuple

from interviewos.models.plan import PreparationPlan, Priority, TopicNode, TopicState


class RecommendationEngine:
    """Provides recommendations on what to study next based on the dynamic plan."""

    PRIORITY_WEIGHTS = {
        Priority.CRITICAL: 4,
        Priority.HIGH: 3,
        Priority.MEDIUM: 2,
        Priority.LOW: 1,
    }

    def get_recommendation(self, plan: PreparationPlan) -> Tuple[TopicNode | None, str]:
        """
        Determine the single best topic to study next.
        Returns a tuple of (RecommendedTopic, ReasonString).
        """
        all_nodes = plan.get_all_nodes()

        # 1. Filter out non-leaf nodes and mastered topics
        candidate_nodes = [
            node for node in all_nodes.values()
            if not node.subtopics and node.state != TopicState.MASTERED
        ]

        if not candidate_nodes:
            return None, "All topics have been mastered! Great job!"

        # 2. Check prerequisite fulfillment for candidates
        # A topic is blocked if any of its prerequisites are in the tree and are NOT mastered
        available_nodes = []
        for node in candidate_nodes:
            is_blocked = False
            for prereq_id in node.prerequisites:
                prereq_node = all_nodes.get(prereq_id)
                # If prereq exists and mastery is too low (< 80)
                if prereq_node and prereq_node.mastery_score < 80.0:
                    is_blocked = True
                    break
            
            if not is_blocked:
                available_nodes.append(node)

        # If all candidates are blocked by prereqs, we might need to recommend 
        # a prerequisite itself (which should theoretically be in the candidate_nodes 
        # and unblocked, unless there's a circular dependency).
        # We will fallback to all candidates if available_nodes is empty (safety net).
        if not available_nodes:
            available_nodes = candidate_nodes

        # 3. Score and sort candidates
        # We want to prioritize:
        # - High JD Priority (Critical > High > Medium > Low)
        # - Low mastery (needs review or completely unstarted)
        
        def score_node(node: TopicNode) -> float:
            priority_score = self.PRIORITY_WEIGHTS.get(node.priority, 1) * 100
            
            # Inverse mastery score: lower mastery means higher need
            mastery_need = 100 - node.mastery_score
            
            # Boost if specifically marked as NEEDS_REVIEW
            review_boost = 50 if node.state == TopicState.NEEDS_REVIEW else 0
            
            return priority_score + mastery_need + review_boost

        available_nodes.sort(key=score_node, reverse=True)
        best_node = available_nodes[0]

        # 4. Generate explainable reasoning
        reasons = []
        if best_node.state == TopicState.NEEDS_REVIEW:
            reasons.append("Recent assessments indicate this area needs review.")
        elif best_node.mastery_score < 20:
            reasons.append(f"Mastery is very low ({best_node.mastery_score}%).")
        else:
            reasons.append(f"Current mastery is at {best_node.mastery_score}%.")

        if best_node.priority in (Priority.CRITICAL, Priority.HIGH):
            reasons.append(f"This topic is a {best_node.priority.value} priority for the target role.")
            
        reason_str = " ".join(reasons)
        
        return best_node, reason_str
