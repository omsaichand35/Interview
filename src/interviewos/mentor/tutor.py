from interviewos.llm import LLMClient
from interviewos.models import LearnerState
from interviewos.models.plan import PreparationPlan


class Tutor:
    """Teaching and learning-evaluation component."""

    SYSTEM_PROMPT = """
You are the InterviewOS AI Mentor.

Your job is to prepare a candidate for a specific job interview.

You have access to:
- the candidate's learning plan
- the candidate's current learning state
- retrieved knowledge
- conversation history

Your behavior must be adaptive.

When teaching:

1. Explain concepts clearly.
2. Start from the candidate's apparent level.
3. Connect concepts to the target job.
4. Use examples.
5. Highlight common interview traps.
6. Ask questions when useful.
7. Do not overwhelm the candidate with unrelated material.

When evaluating an answer:

1. Determine whether the candidate understands the concept.
2. Identify incorrect reasoning.
3. Explain the mistake.
4. Give a corrected explanation.
5. Estimate mastery conservatively.
6. Suggest what to study next.

Never claim that the candidate knows something merely because
it appears in their resume.

Do not fabricate information from the retrieved knowledge.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    def respond(
        self,
        message: str,
        state: LearnerState,
        learning_plan: PreparationPlan | None = None,
        context: str = "",
        conversation: str = "",
    ) -> str:
        """Generate an adaptive mentor response."""

        plan_text = ""

        if learning_plan:
            plan_text = (
                learning_plan.model_dump_json(
                    indent=2
                )
            )

        state_text = state.model_dump_json(
            indent=2
        )

        prompt = f"""
Candidate message:

{message}

Current learner state:

{state_text}

Learning plan:

{plan_text}

Retrieved knowledge:

<knowledge>
{context}
</knowledge>

Recent conversation:

<conversation>
{conversation}
</conversation>

Respond as the candidate's mentor.

Determine what the candidate needs at this moment.

You may:
- teach the requested concept
- clarify confusion
- ask a follow-up question
- give an interview-style practice question
- evaluate their answer
- recommend the next topic

Do not dump the entire learning plan into the response.

Focus on the current interaction.
"""

        return self.llm.sync_generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
        )