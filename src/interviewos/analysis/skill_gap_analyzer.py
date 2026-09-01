from interviewos.models import (
    JobProfile,
    ResumeProfile,
    Skill,
    SkillGap,
    SkillGapReport,
    SkillEvidence,
)

from .skill_extractor import SkillExtractor


class SkillGapAnalyzer:
    """Compare candidate skills against job requirements."""

    def __init__(
        self,
        skill_extractor: SkillExtractor | None = None,
    ) -> None:
        self.skill_extractor = (
            skill_extractor or SkillExtractor()
        )

    def analyze(
        self,
        resume: ResumeProfile,
        job: JobProfile,
    ) -> SkillGapReport:
        """Generate a skill-gap report."""

        candidate_skills = self._build_candidate_skill_map(
            resume
        )

        required_skills = [
            *job.required_skills,
            *job.preferred_skills,
        ]

        gaps: list[SkillGap] = []
        missing = []
        strengths: list[Skill] = []

        for requirement in required_skills:
            normalized_name = self.skill_extractor.normalize(
                requirement.name
            )

            candidate_skill = candidate_skills.get(
                normalized_name
            )

            if candidate_skill is None:
                if requirement.required:
                    missing.append(requirement)

                gap = SkillGap(
                    skill=requirement.name,
                    candidate_level="unknown",
                    required_level=requirement.expected_level,
                    gap_score=1.0,
                    importance=requirement.importance,
                    priority=self._calculate_priority(
                        gap_score=1.0,
                        importance=requirement.importance,
                        required=requirement.required,
                    ),
                    reasoning=(
                        "The skill is required by the job "
                        "description but was not identified "
                        "in the resume."
                    ),
                )

                gaps.append(gap)
                continue

            gap_score = self.skill_extractor.calculate_gap(
                candidate_skill.level,
                requirement.expected_level,
            )

            if gap_score == 0:
                strengths.append(candidate_skill)
                continue

            evidence = [
                SkillEvidence(
                    skill=candidate_skill.name,
                    evidence=evidence_text,
                    source="resume",
                )
                for evidence_text in candidate_skill.evidence
            ]

            gap = SkillGap(
                skill=requirement.name,
                candidate_level=candidate_skill.level,
                required_level=requirement.expected_level,
                gap_score=gap_score,
                importance=requirement.importance,
                priority=self._calculate_priority(
                    gap_score=gap_score,
                    importance=requirement.importance,
                    required=requirement.required,
                ),
                reasoning=(
                    "The candidate demonstrates some "
                    "evidence of this skill, but the detected "
                    "proficiency is below the job requirement."
                ),
                evidence=evidence,
            )

            gaps.append(gap)

        return SkillGapReport(
            gaps=gaps,
            strengths=strengths,
            missing_skills=missing,
        )

    def _build_candidate_skill_map(
        self,
        resume: ResumeProfile,
    ) -> dict[str, Skill]:
        """Build a normalized candidate skill lookup."""

        result: dict[str, Skill] = {}

        for skill in resume.skills:
            normalized = self.skill_extractor.normalize(
                skill.name
            )

            result[normalized] = skill

        return result

    @staticmethod
    def _calculate_priority(
        gap_score: float,
        importance: float,
        required: bool,
    ) -> str:
        """Calculate learning priority."""

        priority_score = gap_score * importance

        if required and priority_score >= 0.7:
            return "critical"

        if priority_score >= 0.6:
            return "high"

        if priority_score >= 0.3:
            return "medium"

        return "low"