import uuid

from interviewos.models.plan import PreparationPlan, TopicNode, AssessmentRecord, Priority
from interviewos.models.learning import LearningGap
from interviewos.planning.mastery_engine import MasteryEngine
from interviewos.planning.priority_engine import PriorityEngine


class LearningPlanUpdater:
    """Updates a PreparationPlan based on LearningGaps identified from interviews."""

    def __init__(self):
        self.mastery_engine = MasteryEngine()
        self.priority_engine = PriorityEngine()

    def update_plan(self, plan: PreparationPlan, gaps: list[LearningGap]) -> PreparationPlan:
        """Apply learning gaps to the preparation plan."""
        
        all_nodes = plan.get_all_nodes()
        nodes_by_title = {node.title.lower(): node for node in all_nodes.values()}
        
        for gap in gaps:
            # 1. Find or create the topic node
            topic_lower = gap.topic.lower()
            if topic_lower in nodes_by_title:
                node = nodes_by_title[topic_lower]
            else:
                # Need to create a new node. We'll append it as a root topic.
                node = TopicNode(
                    id=uuid.uuid4(),
                    title=gap.topic,
                    mastery_score=gap.current_score * 100.0,
                )
                plan.topics.append(node)
                nodes_by_title[topic_lower] = node
                
            # 2. Add AssessmentRecord
            # We map the 0.0-1.0 gap score to 0.0-100.0 for the AssessmentRecord
            notes = f"Identified in {gap.source_round} interview. " + " ".join(gap.evidence)
            record = AssessmentRecord(
                score=gap.current_score * 100.0,
                context=f"Interview Performance ({gap.source_round})",
                notes=notes.strip()
            )
            node.assessment_history.append(record)
            
            # 3. Apply manual priority bump if needed
            # Priority enum in plan.py has LOW, MEDIUM, HIGH, CRITICAL
            gap_priority_value = gap.priority.value.lower()
            if gap_priority_value in ("high", "critical"):
                # We can manually override priority, though priority_engine will also run
                if gap_priority_value == "critical":
                    node.priority = Priority.CRITICAL
                else:
                    node.priority = Priority.HIGH
                    
        # 4. Recalculate Mastery using the engine (this gracefully averages the new scores)
        self.mastery_engine.recalculate_plan(plan)
        
        # 5. Recalculate Priorities
        self.priority_engine.update_priorities(plan)
        
        # We re-apply gap priorities just to be absolutely sure the engine didn't wipe our critical manual flags
        for gap in gaps:
            gap_priority_value = gap.priority.value.lower()
            if gap_priority_value in ("high", "critical"):
                node = nodes_by_title.get(gap.topic.lower())
                if node:
                    if gap_priority_value == "critical":
                        node.priority = Priority.CRITICAL
                    elif node.priority not in (Priority.CRITICAL, Priority.HIGH):
                        node.priority = Priority.HIGH

        return plan

    def format_plan(self, plan: PreparationPlan) -> str:
        """Format the updated learning plan into a readable string."""
        output = ["# UPDATED LEARNING PLAN\n"]
        
        nodes = list(plan.get_all_nodes().values())
        
        # Group by priority
        critical = [n for n in nodes if n.priority == Priority.CRITICAL]
        high = [n for n in nodes if n.priority == Priority.HIGH]
        medium = [n for n in nodes if n.priority == Priority.MEDIUM]
        low = [n for n in nodes if n.priority == Priority.LOW]
        
        def _format_group(group_name, node_list, start_idx=1):
            if not node_list:
                return "", start_idx
            
            res = [f"{group_name}"]
            idx = start_idx
            for n in node_list:
                res.append(f"{idx}. {n.title}")
                res.append(f"   Mastery: {n.mastery_score:.0f}%")
                
                # Try to extract reason from latest assessment
                if n.assessment_history:
                    latest = sorted(n.assessment_history, key=lambda a: a.timestamp, reverse=True)[0]
                    if "Interview" in str(latest.context):
                        res.append(f"   Reason: {latest.context} weakness")
                        
                res.append("")
                idx += 1
            return "\n".join(res), idx
            
        idx = 1
        for group, group_nodes in [
            ("CRITICAL PRIORITY", critical),
            ("HIGH PRIORITY", high),
            ("MEDIUM PRIORITY", medium),
            ("COMPLETED / STRONG / LOW PRIORITY", low),
        ]:
            formatted, idx = _format_group(group, group_nodes, idx)
            if formatted:
                output.append(formatted)
                
        return "\n".join(output)
