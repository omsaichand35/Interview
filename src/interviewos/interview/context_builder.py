from interviewos.models import JobProfile


from .context import InterviewContext
from .session import InterviewSession

from interviewos.interview.project.profile import (
    ProjectProfile,
)
from interviewos.interview.project.index import ProjectEvidenceIndex


class InterviewContextBuilder:
    """Build context supplied to the interviewer."""

    def build(
        self,
        job: JobProfile,
        session: InterviewSession,
        resume_context: str | None = None,
        project_profile: ProjectProfile | None = None,
        additional_instructions: str = "",
) -> InterviewContext:
        """Construct interview context."""

        return InterviewContext(
            job=job,
            session=session,
            resume_context=resume_context,
            project_profile=project_profile,
            additional_instructions=(
                additional_instructions
            ),
        )

    def with_project(
            self,
            context: InterviewContext,
            project: ProjectProfile,
    ) -> InterviewContext:
        """Attach project analysis to interview context."""

        context.project_context = (
            project.model_dump_json(
                indent=2
            )
        )
        context.project_evidence_index = ProjectEvidenceIndex(evidence=project.evidence)

        return context