from interviewos.analysis import ResumeAnalyzer
from interviewos.llm import LLMClient, LLMProvider
from interviewos.models import Document, DocumentMetadata


class FakeLLMProvider(LLMProvider):

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        return """
        {
            "candidate_name": "Test Candidate",
            "summary": "Computer Science student.",
            "skills": [
                {
                    "name": "Python",
                    "level": "advanced",
                    "years_experience": null,
                    "evidence": ["Python project experience"]
                }
            ],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
            "raw_text": null
        }
        """


def test_resume_analyzer_returns_profile() -> None:

    document = Document(
        id="test-document",
        content="Python developer with project experience.",
        metadata=DocumentMetadata(
            source="test",
            filename="resume.txt",
            file_type="text/plain",
        ),
    )

    client = LLMClient(FakeLLMProvider())

    analyzer = ResumeAnalyzer(client)

    result = analyzer.analyze(document)

    assert result.candidate_name == "Test Candidate"
    assert len(result.skills) == 1
    assert result.skills[0].name == "Python"