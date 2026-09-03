from uuid import uuid4

from pydantic import BaseModel, Field

from interviewos.llm import LLMClient
from interviewos.models import JobProfile, ResumeProfile, SkillGapReport
from interviewos.models.plan import PreparationPlan, Priority, TopicNode, TopicState


class InitialTopic(BaseModel):
    title: str = Field(description="Name of the topic or subtopic")
    mastery_score: float = Field(description="Estimated mastery score 0-100 based on resume and gap analysis")
    priority: str = Field(description="low, medium, high, or critical based on job description")
    subtopics: list["InitialTopic"] = Field(default_factory=list, description="Subtopics breaking down this topic if it requires granularity")


class InitialPlanStructure(BaseModel):
    goal: str = Field(description="The primary interview or learning goal")
    topics: list[InitialTopic] = Field(description="Top-level topics")


class PlanGenerator:
    """Uses the LLM to generate a hierarchical PreparationPlan."""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def generate_initial_plan(
        self,
        resume: ResumeProfile,
        job: JobProfile,
        skill_gap_report: SkillGapReport,
    ) -> PreparationPlan:
        """Generate the hierarchical plan using LLM."""

        system_prompt = (
            "You are an expert technical interviewer and mentor. "
            "Given a candidate's resume, target job description, and a skill gap report, "
            "generate a hierarchical preparation plan. "
            "Break down complex topics into subtopics. Assign a mastery score (0-100) and priority "
            "(low, medium, high, critical) to each node based on the gap analysis. "
            "Do not just create a flat list. If a topic like 'Python' or 'Machine Learning' is present, "
            "break it down into specific fundamental subtopics."
        )

        prompt = (
            f"Candidate: {resume.candidate_name}\n"
            f"Role: {job.title}\n\n"
            "Skill Gaps:\n"
        )
        for gap in skill_gap_report.gaps:
            prompt += f"- {gap.skill} (Gap: {gap.gap_score}, Priority: {gap.priority})\n"

        prompt += """
Return a JSON object matching this exact structure:

{
    "goal": "Prepare for Senior Backend Engineer role at TechCorp",
    "topics": [
        {
            "title": "Python & System Design",
            "mastery_score": 65,
            "priority": "critical",
            "subtopics": [
                {
                    "title": "Advanced OOP & Design Patterns",
                    "mastery_score": 60,
                    "priority": "high",
                    "subtopics": []
                },
                {
                    "title": "System Architecture & Scalability",
                    "mastery_score": 55,
                    "priority": "critical",
                    "subtopics": []
                }
            ]
        },
        {
            "title": "Databases & SQL",
            "mastery_score": 70,
            "priority": "high",
            "subtopics": [
                {
                    "title": "Query Optimization & Indexing",
                    "mastery_score": 65,
                    "priority": "high",
                    "subtopics": []
                }
            ]
        }
    ]
}

IMPORTANT: Return ONLY valid JSON, no markdown or schema metadata.
"""

        response = self.llm.sync_generate_structured(
            prompt=prompt,
            system_prompt=system_prompt,
            model=InitialPlanStructure
        )

        plan = PreparationPlan(
            candidate_name=resume.candidate_name,
            goal=response.goal,
        )

        plan.topics = [self._convert_node(t) for t in response.topics]
        return plan

    def _convert_node(self, initial_topic: InitialTopic) -> TopicNode:
        """Convert LLM simplified node into full Domain TopicNode."""
        # Map priority string safely
        priority_map = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM,
            "high": Priority.HIGH,
            "critical": Priority.CRITICAL,
        }
        priority = priority_map.get(initial_topic.priority.lower(), Priority.MEDIUM)

        node = TopicNode(
            id=uuid4(),
            title=initial_topic.title,
            mastery_score=initial_topic.mastery_score,
            priority=priority,
            state=TopicState.NOT_STARTED,
            subtopics=[self._convert_node(sub) for sub in initial_topic.subtopics],
        )
        
        # If mastery is high, we can mark it as MASTERED immediately
        if node.mastery_score >= 90:
            node.state = TopicState.MASTERED
            
        return node
