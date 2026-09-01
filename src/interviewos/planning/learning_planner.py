from interviewos.core.constants import DEFAULT_PREREQUISITES
from interviewos.models import (
    JobProfile,
    LearningPlan,
    ResumeProfile,
    SkillGapReport,
)

from .prerequisite_graph import PrerequisiteGraph
from .roadmap_builder import RoadmapBuilder


class LearningPlanner:
    """Generate a personalized learning plan."""

    def __init__(
        self,
        prerequisite_graph: PrerequisiteGraph | None = None,
        roadmap_builder: RoadmapBuilder | None = None,
    ) -> None:
        self.graph = prerequisite_graph or PrerequisiteGraph(
            DEFAULT_PREREQUISITES
        )

        self.roadmap_builder = (
            roadmap_builder or RoadmapBuilder()
        )

    def create_plan(
        self,
        resume: ResumeProfile,
        job: JobProfile,
        skill_gap_report: SkillGapReport,
    ) -> LearningPlan:
        """Create a learning plan for a candidate."""

        topics = [
            gap.skill
            for gap in skill_gap_report.gaps
        ]

        ordered_topics = self.graph.get_learning_order(
            topics
        )

        modules = self.roadmap_builder.build(
            ordered_topics=ordered_topics,
            report=skill_gap_report,
        )

        total_hours = sum(
            objective.estimated_hours
            for module in modules
            for objective in module.objectives
        )

        goals = self._build_goals(
            skill_gap_report
        )

        return LearningPlan(
            candidate_name=resume.candidate_name,
            target_role=job.title,
            modules=modules,
            total_estimated_hours=round(
                total_hours,
                1,
            ),
            goals=goals,
        )

    @staticmethod
    def _build_goals(
        report: SkillGapReport,
    ) -> list[str]:
        """Create high-level learning goals."""

        goals: list[str] = []

        for gap in report.gaps:
            if gap.priority in {
                "critical",
                "high",
            }:
                goals.append(
                    f"Improve {gap.skill} to the "
                    f"required level."
                )

        for skill in report.strengths:
            goals.append(
                f"Maintain proficiency in {skill.name}."
            )

        return goals