from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TopicState(StrEnum):
    """Meaningful states for a learning topic."""

    NOT_STARTED = "not_started"
    LEARNING = "learning"
    PRACTICING = "practicing"
    NEEDS_REVIEW = "needs_review"
    MASTERED = "mastered"


class Priority(StrEnum):
    """Priority levels for studying."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssessmentRecord(BaseModel):
    """History of an assessment for a topic."""

    score: float = Field(ge=0.0, le=100.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    context: str | None = None
    notes: str | None = None


class TopicNode(BaseModel):
    """Recursive domain model representing a topic or subtopic."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    
    # Base mastery (0-100). If this node has subtopics, this value is 
    # typically computed dynamically based on the children, but we store
    # it here to act as a cache/snapshot.
    mastery_score: float = Field(default=0.0, ge=0.0, le=100.0)
    
    state: TopicState = TopicState.NOT_STARTED
    priority: Priority = Priority.MEDIUM
    
    # Dependencies: IDs of other TopicNodes that must be mastered before this one
    prerequisites: list[UUID] = Field(default_factory=list)
    
    # Recursive child topics
    subtopics: list["TopicNode"] = Field(default_factory=list)
    
    assessment_history: list[AssessmentRecord] = Field(default_factory=list)

    def get_all_descendants(self) -> list["TopicNode"]:
        """Recursively get all subtopics."""
        descendants = []
        for child in self.subtopics:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants


class PreparationPlan(BaseModel):
    """Dynamic Preparation Plan system holding the full mastery tree."""

    id: UUID = Field(default_factory=uuid4)
    candidate_name: str | None = None
    goal: str
    
    overall_mastery: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # The root topics (e.g. Python, Machine Learning)
    topics: list[TopicNode] = Field(default_factory=list)
    
    last_updated: datetime = Field(default_factory=datetime.now)
    
    recommended_next_topic_id: UUID | None = None

    def get_all_nodes(self) -> dict[UUID, TopicNode]:
        """Return a flattened dictionary of all nodes in the tree by ID."""
        nodes: dict[UUID, TopicNode] = {}
        for topic in self.topics:
            nodes[topic.id] = topic
            for desc in topic.get_all_descendants():
                nodes[desc.id] = desc
        return nodes
