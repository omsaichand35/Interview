from pydantic import ValidationError
from interviewos.models import JobProfile
from .models import InterviewPlan, InterviewRoundType

class PlanValidator:
    """Validates an InterviewPlan deterministically."""
    
    @staticmethod
    def validate(plan: InterviewPlan) -> None:
        if not plan.rounds:
            raise ValueError("Interview plan must contain at least one round.")
            
        seen_types = set()
        for r in plan.rounds:
            if r.type in seen_types:
                raise ValueError(f"Duplicate round type detected: {r.type}")
            seen_types.add(r.type)
            
            if r.threshold is not None and not (0.0 <= r.threshold <= 1.0):
                raise ValueError(f"Invalid threshold for round {r.type}: {r.threshold}")
                
            if r.duration_minutes <= 0:
                raise ValueError(f"Invalid duration for round {r.type}: {r.duration_minutes}")
                
        if plan.final_threshold is not None and not (0.0 <= plan.final_threshold <= 1.0):
            raise ValueError(f"Invalid final_threshold: {plan.final_threshold}")

class InterviewPlanGenerator:
    """Generates an InterviewPlan based on a JobProfile using an LLM."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def generate(self, job: JobProfile) -> InterviewPlan:
                
        prompt = f"""
Generate a multi-round Interview Plan for a {job.title}.
The JD emphasizes: {job.summary}

Return a JSON object matching this exact structure:

{{
    "plan_id": "plan_1",
    "role": "{job.title}",
    "rounds": [
        {{
            "round_id": "oa_1",
            "type": "oa",
            "name": "Online Assessment",
            "order": 1,
            "enabled": true,
            "threshold": 0.6,
            "required": true,
            "duration_minutes": 90,
            "configuration": {{"questions": 20, "difficulty": "medium"}}
        }},
        {{
            "round_id": "tech_1",
            "type": "technical",
            "name": "Technical Round 1",
            "order": 2,
            "enabled": true,
            "threshold": 0.65,
            "required": true,
            "duration_minutes": 60,
            "configuration": {{"focus_areas": ["System Design", "Python"]}}
        }},
        {{
            "round_id": "dsa_1",
            "type": "dsa",
            "name": "DSA Round",
            "order": 3,
            "enabled": true,
            "threshold": 0.6,
            "required": true,
            "duration_minutes": 45,
            "configuration": {{"problems": 2, "difficulty": "medium"}}
        }},
        {{
            "round_id": "hr_1",
            "type": "hr",
            "name": "HR & Behavioral",
            "order": 4,
            "enabled": true,
            "threshold": null,
            "required": false,
            "duration_minutes": 30,
            "configuration": {{}}
        }}
    ],
    "created_at": "2024-01-01T00:00:00",
    "configuration": {{}},
    "final_threshold": 0.65
}}

IMPORTANT: Return ONLY valid JSON, no markdown or schema metadata.
"""
        plan = await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert technical recruiter designing interview processes.", model=InterviewPlan)
        
        # Ensure it is valid before returning
        PlanValidator.validate(plan)
        
        return plan
