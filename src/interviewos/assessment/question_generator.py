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
You are an expert technical interviewer creating objective assessment questions.

Generate questions that genuinely test technical understanding and reasoning.

Rules:
1. Every question MUST have EXACTLY 4 options with EXACTLY ONE single correct option.
2. The correct_options array MUST contain EXACTLY ONE option ID.
3. Never create multiple-select questions or questions with more than one correct answer.
4. Questions must be answerable from the stated topic and target role.
5. Do not rely on obscure trivia. Avoid ambiguous wording.
6. Do not make the correct answer obvious from its length.
7. Distractors should be plausible and distinct.
8. Match the requested difficulty.

Return ONLY valid JSON matching the schema.
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

Role: {job.title}
Topic: {topic.name}
Difficulty: {topic.difficulty.value}
Question type: {question_type.value}

Return a JSON object matching this exact structure. The question ID is: {uuid4()}

{{
    "id": "{uuid4()}",
    "question_type": "mcq",
    "topic": "{topic.name}",
    "difficulty": "medium",
    "question": "What is the primary benefit of using a message queue in distributed systems?",
    "options": [
        {{"id": "opt_1", "text": "Decouples producers and consumers, enabling asynchronous communication"}},
        {{"id": "opt_2", "text": "Ensures all requests are processed synchronously"}},
        {{"id": "opt_3", "text": "Eliminates the need for databases"}},
        {{"id": "opt_4", "text": "Provides automatic data encryption"}}
    ],
    "correct_options": ["opt_1"],
    "explanation": "Message queues decouple service components, allowing producers to send messages without waiting for consumers to process them immediately. This enables asynchronous communication and better scalability.",
    "concepts_tested": ["Distributed Systems", "Asynchronous Processing", "Message Queues"]
}}
"""

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=AssessmentQuestion
        )