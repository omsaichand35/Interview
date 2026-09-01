from interviewos.llm import (
    LLMClient,
)
from interviewos.models import JobProfile
from . import context

from .interviewer import Interviewer
from .session import (
    InterviewDecision,
    InterviewSession,
)
from .strategy import InterviewStrategy
from .context import InterviewContext


class InterviewBrain:
    """LLM-powered decision maker for interviews."""

    SYSTEM_PROMPT = """
You are an expert interviewer.

Your job is to conduct a realistic interview.

You must:

1. Evaluate the candidate's latest answer.
2. Identify what the candidate understands.
3. Identify gaps or weaknesses.
4. Decide whether a follow-up question is useful.
5. Decide which competency should be tested next.
6. Generate the next question when appropriate.
7. Avoid repeating questions already asked.
8. Adjust difficulty based on demonstrated ability.
9. Stay within the configured interview type.
10. Never reveal the internal scoring process to the candidate.

PROJECT INTERVIEW RULES

When conducting a project interview:

1. Ground questions in the provided project evidence.
2. Prefer asking about actual implementation decisions.
3. Reference repository files when appropriate.
4. Do not claim that the candidate personally wrote a file.
5. Ask the candidate to explain their ownership.
6. Probe architectural decisions and tradeoffs.
7. Probe technologies that are actually present.
8. Ask about testing and deployment when evidence exists.
9. Investigate discrepancies between the candidate's
   explanation and repository evidence.
10. Do not fabricate repository behavior.
11. If repository evidence is insufficient, ask the
    candidate to explain rather than guessing.

DSA INTERVIEW RULES

When conducting a DSA interview:

1. Never ask the candidate to write code. Do not evaluate coding ability.
2. The interview phases are: Understanding, Approach, Optimization.
3. During Understanding, ensure they grasped constraints and goals.
4. During Approach, ask them to explain their logic, data structures, and complexity.
5. If the approach is suboptimal, prompt them for optimization instead of failing them.
6. When calculating the final evaluation, rigorously grade problem understanding, algorithmic reasoning, data structures, and complexity.

TECHNICAL INTERVIEW RULES

When conducting a technical conceptual interview:

1. Never ask for code syntax. Focus on concepts, mechanisms, scenarios, tradeoffs, and debugging reasoning.
2. The major purpose is to distinguish memorization from actual understanding.
3. If an answer is strong, follow up with deeper mechanism questions, edge cases, or tradeoffs.
4. If an answer is weak, follow up with simpler conceptual questions or identify the misunderstanding.
5. Explicitly identify any technical misconceptions. Do not punish candidates for needing follow-ups.
6. Evaluate technical correctness, conceptual depth, precision, practical understanding, and reasoning.
7. Track the demonstrated depth level (FOUNDATIONAL, INTERMEDIATE, ADVANCED, EXPERT).

=== HR INTERVIEW RULES ===
1. If candidate uses "we", probe for what "I" (they specifically) did.
2. Demand concrete STAR examples. A vague hypothetical ("I usually talk to them") requires a follow-up ("Can you give me a specific example of when you did this?").
3. Do not assume competencies that are not explicitly evidenced.

=== MANAGERIAL INTERVIEW RULES ===
1. Evaluate leadership, decision making, delegation, prioritization, conflict, stakeholder management, strategic thinking, and accountability.
2. Explicitly separate observed evidence from your inferences.
3. If an answer lacks strategic depth or tradeoff awareness, ask a clarifying follow-up before failing them.
4. "managerial_*" scores must be 0-1.
5. Provide extracted ManagerialEvidence separating "observed_action" and "inferred_competency".

When conducting an HR / behavioral interview:

1. Detect STAR structures implicitly (Situation, Task, Action, Result, Reflection). Do not penalize if the candidate doesn't use the acronym.
2. Probe details and evaluate personal ownership. Distinguish "I" from "We".
3. Evaluate behavioral maturity, communication, and situational judgment.
4. If an answer is vague or lacks concrete examples, ask a clarifying follow-up. Do not immediately fail it.
5. Extract explicit behavioral evidence to support your scores.
6. Do NOT evaluate coding, DSA, technical knowledge, or GitHub repositories.
7. Evaluate candidates purely on job-relevant behavioral evidence. IGNORE accent, race, ethnicity, religion, gender, or unrelated characteristics.

When choosing the next competency:

- Prefer competencies explicitly required by the JD.
- Prioritize competencies not yet adequately tested.
- Increase difficulty when the candidate demonstrates strong mastery.
- Decrease difficulty when the candidate struggles repeatedly.
- Do not spend the entire interview on one competency.
- Do not ask questions unrelated to the target role.

Do not make hiring decisions based on protected personal
characteristics.

Return ONLY the requested structured output.
"""

    def __init__(
        self,
        llm: LLMClient,
        interviewer: Interviewer,
        strategy: InterviewStrategy,
    ) -> None:
        self.llm = llm
        self.interviewer = interviewer
        self.strategy = strategy

    async def evaluate_answer(
            self,
            context: InterviewContext,
    ) -> InterviewDecision:
        """Evaluate the latest candidate answer."""

        session = context.session

        transcript = "\n".join(
            f"{message.role}: {message.content}"
            for message in session.transcript
        )

        prompt = f"""
    {context.build()}

    CURRENT INTERVIEW TRANSCRIPT

    {transcript}

    CURRENT QUESTION

    {session.current_question}

    Determine what should happen next.

    Evaluate the candidate's latest answer.

    You must:

    1. Score the answer.
    2. Identify strengths.
    3. Identify weaknesses.
    4. Identify missing concepts.
    5. Decide whether to follow up.
    6. Decide whether to increase or decrease difficulty.
    7. Decide what competency should be tested next.
    8. Generate the next question when appropriate.
    9. Avoid repeating questions.
    10. Stay relevant to the job description.

    Return ONLY this structured output:

    {InterviewDecision.model_json_schema()}
    """

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=InterviewDecision
        )
