from interviewos.llm import LLMClient
from interviewos.models import (
    LearnerState,
    MentorDecision,
)
from interviewos.models.plan import PreparationPlan


class MentorAgent:
    """Decide what the mentor should do next."""

    SYSTEM_PROMPT = """
You are the decision-making component of InterviewOS.

Your job is NOT to answer the candidate directly.

Your job is to decide what the mentor should do next.

Available actions:

TEACH
- Explain a concept to the candidate.

PRACTICE
- Generate a practice question.

EVALUATE
- Evaluate an answer the candidate has provided.

REVIEW
- Revisit a weak topic.

MOVE_FORWARD
- Move to the next appropriate learning topic.

CLARIFY
- Ask the candidate for clarification when their intent
  or question is ambiguous.

Use the learner state and learning plan when making decisions.

Prefer REVIEW when the candidate repeatedly struggles with
a topic.

Prefer MOVE_FORWARD when the candidate demonstrates strong
understanding.

Do not choose actions unrelated to interview preparation.

Return ONLY valid JSON.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    def decide(
        self,
        message: str,
        state: LearnerState,
        learning_plan: PreparationPlan | None = None,
    ) -> MentorDecision:
        """Determine the next mentor action."""

        plan_text = ""

        if learning_plan:
            plan_text = learning_plan.model_dump_json(
                indent=2
            )

        prompt = f"""
Determine the appropriate next action for the mentor.

Candidate message: {message}

Learner state:

<learner_state>
{state.model_dump_json(indent=2)}
</learner_state>

Learning plan:

<learning_plan>
{plan_text}
</learning_plan>

Return a JSON object matching this exact structure:

{{
    "action": "practice",
    "topic": "Binary Search Trees",
    "reasoning": "The candidate needs more practice with tree algorithms before moving to graph algorithms",
    "difficulty": "medium",
    "retrieval_query": "BST insertion, deletion, and traversal examples"
}}

Possible actions: teach, practice, evaluate, review, move_forward, clarify

IMPORTANT: Return ONLY valid JSON, no markdown or schema metadata.
"""

        return self.llm.sync_generate_structured(prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT, model=MentorDecision)