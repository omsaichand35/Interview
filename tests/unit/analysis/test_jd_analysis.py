from interviewos.analysis import JobAnalyzer
from interviewos.llm import LLMClient, LLMProvider
from interviewos.models import Document, DocumentMetadata


class FakeJobLLMProvider(LLMProvider):
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        assert "model_json_schema" not in prompt
        assert '"title": "Senior Backend Engineer"' in prompt
        assert "qualifications" in prompt
        assert "interview_topics" in prompt
        return """
		{
			"title": "Senior Python Engineer",
			"required_skills": [
				{
					"name": "Python",
					"required": true,
					"expected_level": "advanced",
					"importance": 1.0,
					"evidence": ["Build backend services in Python"]
				}
			],
			"preferred_skills": [],
			"responsibilities": [],
			"qualifications": [],
			"interview_topics": []
		}
		"""


def test_job_analyzer_returns_extracted_requirements() -> None:
    document = Document(
        id="test-document",
        content="Senior Python Engineer. Build backend services in Python.",
        metadata=DocumentMetadata(
            source="test",
            filename="job.txt",
            file_type="text/plain",
        ),
    )

    result = JobAnalyzer(LLMClient(FakeJobLLMProvider())).analyze(document)

    assert result.title == "Senior Python Engineer"
    assert len(result.required_skills) == 1
    assert result.required_skills[0].name == "Python"
