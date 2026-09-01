from interviewos.core.exceptions import AnalysisError
from interviewos.llm import LLMClient
from interviewos.models import JobProfile
from interviewos.models.documents import Document


class JobAnalyzer:
    """Analyze a job description using an LLM."""

    SYSTEM_PROMPT = """
You are an expert technical recruiter and job-description analyst.

Analyze the provided job description carefully.

Extract requirements and responsibilities explicitly supported
by the job description.

Distinguish between:
- required skills
- preferred skills
- responsibilities
- qualifications
- likely technical interview topics

Do not invent requirements that are not reasonably supported
by the job description.

Return ONLY valid JSON matching the requested schema.

For skill importance:
- 1.0 means extremely important.
- 0.75 means highly important.
- 0.5 means moderately important.
- 0.25 means minor importance.

For skill level, use:
- beginner
- intermediate
- advanced
- expert
- unknown
"""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def analyze(self, document: Document) -> JobProfile:
        """
        Synchronously analyze an ingested job-description document.
        Wraps analyze_async for use in sync contexts (e.g., CLI startup).
        """
        return self.llm.sync_generate_structured(
            prompt=self._build_prompt(document),
            system_prompt=self.SYSTEM_PROMPT,
            model=JobProfile,
        )

    async def analyze_async(self, document: Document) -> JobProfile:
        """
        Async analyze an ingested job-description document.

        Args:
            document: Normalized job-description document.

        Returns:
            Structured JobProfile.
        """

        if not document.content.strip():
            raise AnalysisError(
                "Cannot analyze an empty job description."
            )

        try:
            return await self.llm.generate_structured(
                prompt=self._build_prompt(document),
                system_prompt=self.SYSTEM_PROMPT,
                model=JobProfile
            )

        except Exception as exc:
            if isinstance(exc, AnalysisError):
                raise

            raise AnalysisError(
                "Failed to analyze job description."
            ) from exc

    def _build_prompt(self, document: Document) -> str:
        if not document.content.strip():
            raise AnalysisError(
                "Cannot analyze an empty job description."
            )

        return f"""
Analyze the following job description.

Return a JSON object matching this structure:

{JobProfile.model_json_schema()}

Job description:

--- BEGIN JOB DESCRIPTION ---
{document.content}
--- END JOB DESCRIPTION ---
"""