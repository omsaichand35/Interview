from uuid import uuid4

from interviewos.llm import (
    LLMClient,
)
from interviewos.models import (
    AssessmentQuestion,
    AssessmentTopic,
    Difficulty,
    JobProfile,
    QuestionType,
)


class QuestionGenerator:
    """Generate objective assessment questions."""

    SYSTEM_PROMPT = """
You are an expert technical interviewer creating objective
assessment questions.

Generate questions that genuinely test understanding.

Rules:

1. Questions must be answerable from the stated topic.
2. Do not rely on obscure trivia.
3. Avoid ambiguous wording.
4. Do not make the correct answer obvious from its length.
5. Distractors should be plausible.
6. Match the requested difficulty.
7. Test reasoning and practical understanding when possible.
8. Do not use information unrelated to the target role.

For MCQs:
- provide exactly one correct option.

For multiple-select:
- provide at least two options and clearly identify
  all correct options.

Return ONLY valid JSON.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    async def generate(
        self,
        topic: AssessmentTopic,
        job: JobProfile,
        question_type: QuestionType = QuestionType.MCQ,
    ) -> AssessmentQuestion:
        """Generate one assessment question."""

        prompt = f"""
Generate one objective assessment question.

Role:
{job.title}

Topic:
{topic.name}

Difficulty:
{topic.difficulty.value}

Question type:
{question_type.value}

Return an object matching:

{AssessmentQuestion.model_json_schema()}

The question ID should be:

{uuid4()}
"""

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=AssessmentQuestion
        )