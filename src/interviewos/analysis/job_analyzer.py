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

Return ONLY a JSON object containing the extracted job data. Do not return JSON
Schema metadata such as `$defs`, `properties`, or `required`.

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
            raise AnalysisError("Cannot analyze an empty job description.")

        try:
            return await self.llm.generate_structured(
                prompt=self._build_prompt(document),
                system_prompt=self.SYSTEM_PROMPT,
                model=JobProfile,
            )

        except Exception as exc:
            if isinstance(exc, AnalysisError):
                raise

            raise AnalysisError("Failed to analyze job description.") from exc

    def _build_prompt(self, document: Document) -> str:
        if not document.content.strip():
            raise AnalysisError("Cannot analyze an empty job description.")

        return f"""
Analyze the following job description and extract structured job profile data.

IMPORTANT RULES:
1. The `title` field must be the actual job title from the document (e.g., "Senior Python Developer"), NEVER the string "JobProfile"
2. qualifications, interview_topics are lists of PLAIN STRINGS, NOT objects
3. responsibilities is a list of objects with "description" and "skills" fields
4. Extract every supported skill with evidence from the job description
5. Do not invent information not present in the job description

Return ONLY a valid JSON object matching this EXACT structure:

{{
    "title": "Senior Backend Engineer",
    "company": null,
    "location": null,
    "employment_type": null,
    "summary": null,
    "required_skills": [
        {{"name": "Python", "required": true, "expected_level": "advanced", "importance": 1.0, "evidence": ["Requires 5+ years Python"]}}
    ],
    "preferred_skills": [
        {{"name": "Docker", "required": false, "expected_level": "intermediate", "importance": 0.75, "evidence": ["Nice to have Docker experience"]}}
    ],
    "responsibilities": [
        {{"description": "Design and maintain scalable backend systems", "skills": ["System Design", "Python", "Databases"]}}
    ],
    "qualifications": [
        "Bachelor's degree in Computer Science or related field",
        "5+ years backend development experience"
    ],
    "interview_topics": [
        "System Design",
        "Python",
        "SQL Databases",
        "API Design"
    ],
    "raw_text": null
}}

Job description:

--- BEGIN JOB DESCRIPTION ---
{document.content}
--- END JOB DESCRIPTION ---
"""
