from interviewos.models import JobProfile

from ..strategy import InterviewStrategy


class ProjectInterviewStrategy(
    InterviewStrategy
):
    """Project-based interview strategy."""

    def competencies(self) -> list[str]:
        return [
            "project_understanding",
            "technical_ownership",
            "architecture",
            "implementation",
            "tradeoffs",
            "debugging",
            "testing",
            "deployment",
            "communication",
        ]

    def build_context(
        self,
        job: JobProfile,
    ) -> str:
        return f"""
Conduct a project-based interview for:

{job.title}

Questions should be grounded in the
candidate's actual repository.

Do not assume the candidate authored
code simply because it exists in the
repository.

Ask the candidate to explain relevant
parts of the project and use repository
evidence to generate follow-up questions.
""".strip()