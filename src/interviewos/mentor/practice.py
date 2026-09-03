from interviewos.llm import LLMClient
from interviewos.models import (
    LearnerState,
    PracticeQuestion,
)


class PracticeGenerator:
    """Generate learning-oriented practice questions."""

    SYSTEM_PROMPT = """
You are an expert technical interviewer creating practice
questions for an interview candidate.

Generate one question at a time.

The question should:

- test understanding rather than memorization
- match the candidate's current level
- relate to the target role when possible
- focus on the requested topic
- have a clear expected concept set

Return ONLY valid JSON.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    def generate(
        self,
        topic: str,
        state: LearnerState,
        context: str = "",
        difficulty: str = "medium",
    ) -> PracticeQuestion:
        """Generate a practice question."""

        prompt = f"""
Generate one practice question.

Topic: {topic}
Difficulty: {difficulty}

Learner state:

{state.model_dump_json(indent=2)}

Relevant knowledge:

<knowledge>
{context}
</knowledge>

Return a JSON object matching this exact structure:

{{
    "question": "Explain the difference between depth-first search and breadth-first search. When would you use one over the other?",
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "expected_concepts": ["Graph traversal", "Time complexity", "Space complexity", "Use case selection"]
}}

IMPORTANT: Return ONLY valid JSON, no markdown or schema metadata.
"""

        return self.llm.sync_generate_structured(prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT, model=PracticeQuestion)