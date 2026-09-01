from dataclasses import dataclass, field

from interviewos.models import JobProfile
from .project import ProjectProfile, ProjectEvidenceIndex

from .session import InterviewSession


@dataclass
class InterviewContext:
    """Context available to the interviewer."""

    job: JobProfile

    session: InterviewSession

    additional_instructions: str = ""

    resume_context: str | None = None

    project_context: str | None = None

    covered_competencies: list[str] = field(
        default_factory=list,
    )

    covered_topics: list[str] = field(
        default_factory=list,
    )

    project_profile: ProjectProfile | None = None
    
    project_evidence_index: 'ProjectEvidenceIndex | None' = None

    def build(self) -> str:
        """Build a textual context for the interviewer."""

        sections = [
            self._job_context(),
            self._session_context(),
        ]

        if self.resume_context:
            sections.append(
                self._resume_context()
            )

        if (
                self.project_profile is not None
                or self.project_context
        ):
            sections.append(
                self._project_context()
            )

        if self.additional_instructions:
            sections.append(
                "ADDITIONAL INSTRUCTIONS\n"
                f"{self.additional_instructions}"
            )

        return "\n\n".join(sections)

    def _job_context(self) -> str:
        return (
            "JOB CONTEXT\n"
            f"Role: {self.job.title}\n"
            f"{self.job.model_dump_json(indent=2)}"
        )

    def _session_context(self) -> str:
        return (
            "INTERVIEW STATE\n"
            f"Type: "
            f"{self.session.interview_type.value}\n"
            f"Difficulty: "
            f"{self.session.difficulty}\n"
            f"Questions asked: "
            f"{self.session.questions_asked}\n"
            f"Covered competencies: "
            f"{self.covered_competencies}\n"
            f"Covered topics: "
            f"{self.covered_topics}"
        )

    def _resume_context(self) -> str:
        return (
            "RESUME CONTEXT\n"
            f"{self.resume_context}"
        )

    def _project_context(
            self,
    ) -> str:
        """Build project context."""

        if self.project_profile is None:
            return ""

        return (
            "PROJECT ANALYSIS\n"
            f"{self.project_profile.model_dump_json(indent=2)}"
        )