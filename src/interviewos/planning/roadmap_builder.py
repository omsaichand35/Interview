from interviewos.models import (
    LearningModule,
    LearningObjective,
    LearningPriority,
    SkillGapReport,
)


class RoadmapBuilder:
    """Build a structured roadmap from skill gaps."""

    def build(
        self,
        ordered_topics: list[str],
        report: SkillGapReport,
    ) -> list[LearningModule]:
        """Create learning modules from ordered topics."""

        gaps_by_skill = {
            gap.skill.strip().lower(): gap
            for gap in report.gaps
        }

        modules: list[LearningModule] = []

        for index, topic in enumerate(
            ordered_topics,
            start=1,
        ):
            gap = gaps_by_skill.get(
                topic.lower()
            )

            if gap is None:
                # Prerequisite topics may not be explicitly
                # present in the skill-gap report.
                objective = LearningObjective(
                    title=f"Learn {topic.title()}",
                    description=(
                        f"Build the foundational knowledge "
                        f"required for {topic.title()}."
                    ),
                    related_skills=[topic],
                    priority=LearningPriority.MEDIUM,
                    estimated_hours=2.0,
                    prerequisites=[],
                )
            else:
                priority = self._map_priority(
                    gap.priority
                )

                objective = LearningObjective(
                    title=f"Improve {gap.skill}",
                    description=(
                        f"Close the identified gap in "
                        f"{gap.skill} and reach the level "
                        f"required for the target role."
                    ),
                    related_skills=[gap.skill],
                    priority=priority,
                    estimated_hours=self._estimate_hours(
                        gap.gap_score,
                        priority,
                    ),
                    prerequisites=[],
                )

            modules.append(
                LearningModule(
                    title=topic.title(),
                    description=objective.description,
                    objectives=[objective],
                    order=index,
                )
            )

        return modules

    @staticmethod
    def _map_priority(
        priority: str,
    ) -> LearningPriority:
        mapping = {
            "low": LearningPriority.LOW,
            "medium": LearningPriority.MEDIUM,
            "high": LearningPriority.HIGH,
            "critical": LearningPriority.CRITICAL,
        }

        return mapping.get(
            priority.lower(),
            LearningPriority.MEDIUM,
        )

    @staticmethod
    def _estimate_hours(
        gap_score: float,
        priority: LearningPriority,
    ) -> float:
        """Estimate study time based on the size of the gap."""

        base_hours = 1.5 + (gap_score * 4.5)

        if priority == LearningPriority.CRITICAL:
            base_hours *= 1.25

        return round(base_hours, 1)