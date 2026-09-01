from pydantic import BaseModel, Field

from .repository import RepositorySnapshot, RepositoryFile
from .evidence import ProjectEvidence
from .retrieval import RetrievalRequest


class ProjectAnalysisState(BaseModel):
    """Tracks the state of an agentic project analysis session."""

    repository: RepositorySnapshot
    
    files_retrieved: list[RepositoryFile] = Field(default_factory=list)
    
    files_analyzed: set[str] = Field(default_factory=set)
    
    evidence_discovered: list[ProjectEvidence] = Field(default_factory=list)
    
    retrieval_requests: list[RetrievalRequest] = Field(default_factory=list)
    
    iterations: int = 0
    
    unresolved_questions: list[str] = Field(default_factory=list)
    
    sufficient_evidence: bool = False
    
    max_iterations: int = 5
