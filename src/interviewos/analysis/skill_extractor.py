from interviewos.models import Skill, SkillLevel


class SkillExtractor:
    """Utilities for normalizing and comparing skill names."""

    _ALIASES: dict[str, str] = {
        "python3": "python",
        "py": "python",
        "pytorch": "pytorch",
        "torch": "pytorch",
        "tensorflow": "tensorflow",
        "tf": "tensorflow",
        "machine learning": "machine learning",
        "ml": "machine learning",
        "deep learning": "deep learning",
        "dl": "deep learning",
        "computer vision": "computer vision",
        "cv": "computer vision",
        "natural language processing": "nlp",
        "nlp": "nlp",
        "structured query language": "sql",
        "sql": "sql",
        "c plus plus": "c++",
        "cpp": "c++",
    }

    def normalize(self, skill_name: str) -> str:
        """Normalize a skill name for comparison."""

        normalized = " ".join(
            skill_name.strip().lower().split()
        )

        return self._ALIASES.get(
            normalized,
            normalized,
        )

    def normalize_level(self, level: SkillLevel) -> int:
        """Convert a skill level into an ordered numeric value."""

        levels = {
            SkillLevel.UNKNOWN: 0,
            SkillLevel.BEGINNER: 1,
            SkillLevel.INTERMEDIATE: 2,
            SkillLevel.ADVANCED: 3,
            SkillLevel.EXPERT: 4,
        }

        return levels[level]

    def calculate_gap(
        self,
        candidate_level: SkillLevel,
        required_level: SkillLevel,
    ) -> float:
        """
        Calculate normalized skill gap.

        Returns:
            Value between 0 and 1.
            0 means no detected gap.
            1 means maximum gap.
        """

        candidate = self.normalize_level(candidate_level)
        required = self.normalize_level(required_level)

        if required == 0:
            return 0.0

        if candidate >= required:
            return 0.0

        return min(
            1.0,
            (required - candidate) / required,
        )