from enum import Enum
from pydantic import BaseModel


class EvidenceType(str, Enum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"


class ProjectEvidence(BaseModel):
    """Evidence discovered in a repository."""

    category: str = "General"

    description: str = ""

    type: EvidenceType = EvidenceType.OBSERVED

    source_file: str | None = None
    
    source_location: str | None = None
    
    snippet: str | None = None

    confidence: float = 1.0