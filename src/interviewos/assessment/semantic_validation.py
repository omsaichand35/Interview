from interviewos.llm import (
    LLMClient,
)
from interviewos.models import (
    AssessmentQuestion,
    JobProfile,
    QuestionValidationResult,
)


class SemanticQuestionValidator:
    """Validate question quality using an LLM."""

    SYSTEM_PROMPT = """
You are a senior technical assessment reviewer.

Review a generated assessment question.

Determine whether:

1. The question matches the requested topic.
2. The question matches the target role.
3. The difficulty is appropriate.
4. The question is unambiguous.
5. The correct answer is actually correct.
6. The distractors are plausible.
7. The question tests useful knowledge rather than trivia.
8. The explanation is consistent with the answer.

Be conservative.

If there is meaningful doubt about correctness or ambiguity,
mark the question invalid.

Return ONLY valid JSON.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    async def validate(
        self,
        question: AssessmentQuestion,
        job: JobProfile,
    ) -> QuestionValidationResult:
        """Perform semantic validation."""

        prompt = f"""
Review this generated assessment question.

Target role:

{job.title}

Question:

{question.model_dump_json(indent=2)}

Return:

{QuestionValidationResult.model_json_schema()}
"""

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=QuestionValidationResult
        )