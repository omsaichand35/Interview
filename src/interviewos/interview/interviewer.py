from dataclasses import dataclass

from interviewos.models import JobProfile

from .state import InterviewType


@dataclass
class InterviewerConfig:
    """Configuration for one interviewer instance."""

    interview_type: InterviewType

    difficulty: str = "medium"

    duration_minutes: int = 30

    allow_follow_ups: bool = True

    allow_deep_dive: bool = True

    instructions: str = ""


class Interviewer:
    """Represents the interviewer configuration."""

    def __init__(
        self,
        config: InterviewerConfig,
    ) -> None:
        self.config = config

    def build_system_context(
        self,
        job: JobProfile,
    ) -> str:
        """Build basic interviewer context."""

        return f"""
You are conducting a {self.config.interview_type.value}
interview.

Target role:
{job.title}

Difficulty:
{self.config.difficulty}

Interview duration:
{self.config.duration_minutes} minutes

Additional interviewer instructions:
{self.config.instructions}
""".strip()