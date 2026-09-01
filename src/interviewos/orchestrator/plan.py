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

Create a sequence of rounds (e.g., OA, Technical, DSA, HR).
Provide sensible thresholds between 0.0 and 1.0.

Return ONLY structured JSON matching this schema:
{InterviewPlan.model_json_schema()}
"""
        plan = await self.llm.generate_structured(prompt=prompt,
            system_prompt="You are an expert technical recruiter designing interview processes.", model=InterviewPlan)
        
        # Ensure it is valid before returning
        PlanValidator.validate(plan)
        
        return plan
