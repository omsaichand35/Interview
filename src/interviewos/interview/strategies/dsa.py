from interviewos.models import JobProfile

from ..strategy import InterviewStrategy


class DSAInterviewStrategy(
    InterviewStrategy
):
    """DSA interview strategy."""

    def competencies(self) -> list[str]:
        return [
            "problem_solving",
            "algorithmic_thinking",
            "data_structures",
            "complexity_analysis",
            "communication",
        ]

    def build_context(
        self,
        job: JobProfile,
    ) -> str:
        return (
            f"DSA interview for "
            f"{job.title}."
        )


class DSAProblemGenerator:
    """Generates DSA problems using an LLM."""

    def __init__(self, llm):
        self.llm = llm

    async def generate(self, job: JobProfile, difficulty: str, covered_topics: list[str]) -> 'DSAProblem':
        from interviewos.interview.session import DSAProblem
        
        prompt = f"""
Generate a Data Structures and Algorithms problem for a {job.title}.
The difficulty should be {difficulty}.

Covered topics to avoid: {', '.join(covered_topics) if covered_topics else 'None'}
The JD emphasizes: {job.summary}

The problem must test approach and reasoning, not just memorization.
Return ONLY structured JSON matching this schema:
{DSAProblem.model_json_schema()}
"""
        return await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert technical interviewer designing DSA questions. Ensure problem constraints and examples are clear and well-formed.", model=DSAProblem)


class DSAProblemValidator:
    """Validates generated DSA problems."""

    def validate(self, problem: 'DSAProblem') -> bool:
        if not problem.statement or not problem.title:
            return False
        if not problem.examples:
            return False
        if not problem.expected_complexity:
            return False
        return True