from interviewos.core.exceptions import AnalysisError
from interviewos.llm import LLMClient
from interviewos.models import ResumeProfile
from interviewos.models.documents import Document


class ResumeAnalyzer:
    """Analyze a resume document using an LLM."""

    SYSTEM_PROMPT = """
You are a professional technical recruiter and resume analyst.

Analyze the provided resume carefully.

Extract only information that is supported by the resume:
- Candidate Name (field: candidate_name): Extract the candidate's full name, usually prominently listed at the very top header of the resume.

Do not invent:
- skills
- experience
- projects
- education
- achievements
- technologies
- years of experience

Return ONLY a JSON object containing the extracted resume data. Do not return
JSON Schema metadata such as `$defs`, `properties`, or `required`. Do not use
empty lists when the resume contains matching information.

For skill proficiency:
- Use beginner when evidence is limited.
- Use intermediate when practical usage is demonstrated.
- Use advanced when substantial implementation or experience is demonstrated.
- Use expert only when strong evidence supports it.
- Use unknown when proficiency cannot reasonably be determined.

Evidence must be concise and grounded in the resume.
"""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def analyze(self, document: Document) -> ResumeProfile:
        """
        Analyze an ingested resume document (sync).
        Used by Phase 1 mentor flow which runs outside an event loop.
        """
        if not document.content.strip():
            raise AnalysisError("Cannot analyze an empty resume document.")

        try:
            return self.llm.sync_generate_structured(
                prompt=self._build_prompt(document),
                system_prompt=self.SYSTEM_PROMPT,
                model=ResumeProfile,
            )
        except Exception as exc:
            if isinstance(exc, AnalysisError):
                raise
            raise AnalysisError("Failed to analyze resume.") from exc

    async def analyze_async(self, document: Document) -> ResumeProfile:
        """
        Analyze an ingested resume document (async).
        Used when called from within an already-running event loop (e.g., run_hiring).
        """
        if not document.content.strip():
            raise AnalysisError("Cannot analyze an empty resume document.")

        try:
            return await self.llm.generate_structured(
                prompt=self._build_prompt(document),
                system_prompt=self.SYSTEM_PROMPT,
                model=ResumeProfile,
            )
        except Exception as exc:
            if isinstance(exc, AnalysisError):
                raise
            raise AnalysisError("Failed to analyze resume.") from exc

    def _build_prompt(self, document: Document) -> str:
        return f"""
Analyze the following resume.

Return a JSON object matching this structure. Extract every supported skill,
experience, project, education item, certification, and achievement from the
resume. Use an empty list only when that section is absent:

{{
    "candidate_name": "Full Name or null",
    "summary": "Summary or null",
    "skills": [
        {{"name": "Python", "level": "advanced", "years_experience": null, "evidence": ["Evidence from resume"]}}
    ],
    "education": [],
    "experience": [],
    "projects": [],
    "certifications": [],
    "achievements": [],
    "raw_text": null
}}

Resume:

--- BEGIN RESUME ---
{document.content}
--- END RESUME ---
"""
