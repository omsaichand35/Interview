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
Target difficulty: {difficulty}

Covered topics to avoid: {', '.join(covered_topics) if covered_topics else 'None'}
The JD emphasizes: {job.summary or 'Software Development'}

Return a JSON object matching this exact structure:

{{
    "problem_id": "prob_1",
    "title": "Two Sum",
    "statement": "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to the target. You may assume each input has exactly one solution, and you cannot use the same element twice. Example: Input: nums = [2, 7, 11, 15], target = 9, Output: [0, 1]",
    "difficulty": "easy",
    "topics": ["Hash Table", "Arrays", "Two Pointers"],
    "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
    "examples": [
        {{"input": "nums = [2, 7, 11, 15], target = 9", "output": "[0, 1]"}},
        {{"input": "nums = [3, 2, 4], target = 6", "output": "[1, 2]"}}
    ],
    "expected_complexity": "O(n) time, O(n) space using hash table",
    "hidden_solution_information": "Use a hash table to store values seen so far. For each number, check if target - number exists in the hash table. This enables O(n) time complexity instead of O(n^2) with nested loops."
}}

IMPORTANT: Return ONLY valid JSON, no markdown or schema metadata.
"""
        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt="You are an expert technical interviewer designing DSA questions. Ensure problem constraints and examples are clear and well-formed. Return ONLY a top-level JSON object.",
            model=DSAProblem
        )



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