from interviewos.llm import (
    LLMClient,
)
from interviewos.models import (
    AssessmentBlueprint,
    JobProfile,
)


class AssessmentBlueprintGenerator:
    """Generate an OA blueprint from a job description."""

    SYSTEM_PROMPT = """
You are an expert technical assessment designer.

Create an objective assessment blueprint for a job candidate.

The assessment must be based on the requirements of the job
description, UNLESS the user has specified custom topics.

If custom topics are provided by the user, you MUST prioritize
these topics and their requested weightages to form the blueprint. 
If custom topics are provided, they take precedence over the job description, 
allowing the user to test the candidate on subjects outside the job description.

Do not use the candidate's resume.

Determine:

- important technical topics
- relative topic importance (based on requested weightages if provided)
- number of questions per topic
- appropriate difficulty
- assessment duration
- suitable objective question types

Prioritize skills that are explicitly required by the job, unless overridden
by custom topics.

Do not give excessive weight to optional skills unless the
job description strongly emphasizes them.

Return ONLY valid JSON matching the requested schema.
"""

    def __init__(
        self,
        llm: LLMClient,
    ) -> None:
        self.llm = llm

    async def generate(
        self,
        job: JobProfile,
        total_questions: int = 20,
        duration_minutes: int = 30,
        topics: str | None = None,
    ) -> AssessmentBlueprint:
        """Generate an assessment blueprint."""

        job_text = job.model_dump_json(
            indent=2
        )

        custom_topics_section = ""
        if topics:
            custom_topics_section = f"""
Custom Topics Requested by User:
<custom_topics>
{topics}
</custom_topics>
IMPORTANT: You MUST base the blueprint topics and weights on the <custom_topics> provided above.
"""

        prompt = f"""
Create an OA blueprint for this role.

Job description analysis:

<job>
{job_text}
</job>
{custom_topics_section}
Total questions: {total_questions}
Duration: {duration_minutes} minutes

Return a JSON object matching this exact structure:

{{
    "role": "Senior Backend Engineer",
    "duration_minutes": 30,
    "total_questions": 20,
    "question_types": ["mcq", "multiple_select"],
    "topics": [
        {{
            "name": "System Design",
            "weight": 0.3,
            "question_count": 6,
            "difficulty": "hard"
        }},
        {{
            "name": "Python",
            "weight": 0.25,
            "question_count": 5,
            "difficulty": "medium"
        }},
        {{
            "name": "SQL Databases",
            "weight": 0.25,
            "question_count": 5,
            "difficulty": "medium"
        }},
        {{
            "name": "API Design",
            "weight": 0.2,
            "question_count": 4,
            "difficulty": "medium"
        }}
    ]
}}
"""

        return await self.llm.generate_structured(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=AssessmentBlueprint
        )