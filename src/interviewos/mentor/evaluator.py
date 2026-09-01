from interviewos.llm import LLMClient
from interviewos.models import (
    EvaluationResult,
    LearnerState,
)


class MentorEvaluator:
    """Evaluate candidate responses during learning."""

    SYSTEM_PROMPT = """
You are an expert technical interviewer and teaching evaluator.

Evaluate the candidate's answer fairly and conservatively.

Consider:

- factual correctness
- conceptual understanding
- reasoning
- completeness
- ability to explain the concept
- important missing concepts

Do not require the candidate to use exactly the same wording
as the reference answer.

A candidate can be correct even if their explanation is concise.

However, do not give a high score merely because they mention
the right keywords.

Return ONLY valid JSON matching the requested schema.

Scoring:

0.0 - completely incorrect
0.25 - very limited understanding
0.50 - partial understanding
0.75 - mostly correct
1.0 - strong understanding

Be particularly careful with technical concepts.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    def evaluate(
        self,
        topic: str,
        question: str,
        candidate_answer: str,
        reference_context: str = "",
        state: LearnerState | None = None,
    ) -> EvaluationResult:
        """Evaluate one candidate answer."""

        if not candidate_answer.strip():
            raise ValueError(
                "Candidate answer cannot be empty."
            )

        state_text = ""

        if state:
            state_text = state.model_dump_json(
                indent=2
            )

        prompt = f"""
Evaluate the candidate's answer.

Topic:
{topic}

Question:
{question}

Candidate answer:
{candidate_answer}

Reference knowledge:

<reference>
{reference_context}
</reference>

Current learner state:

<learner_state>
{state_text}
</learner_state>

Return a JSON object matching this schema:

{EvaluationResult.model_json_schema()}

Important:

Evaluate the answer itself.

Do not assume the candidate knows something merely because
their resume or learner state says they studied it.
"""

        return self.llm.sync_generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=EvaluationResult
        )