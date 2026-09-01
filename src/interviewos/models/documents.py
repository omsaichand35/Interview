from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata associated with an ingested document."""

    source: str
    filename: str
    file_type: str
    path: Path | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class Document(BaseModel):
    """Normalized document representation used throughout InterviewOS."""

    id: str
    content: str
    metadata: DocumentMetadata


class DocumentChunk(BaseModel):
    """A chunk of a document used by the RAG pipeline."""

    id: str
    document_id: str
    content: str

    chunk_index: int = Field(ge=0)

    metadata: dict[str, str] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """A retrieved knowledge chunk with its relevance score."""

    chunk: DocumentChunk
    score: float


class RAGResponse(BaseModel):
    """Grounded response produced by the RAG system."""

    answer: str

    sources: list[RetrievalResult] = Field(
        default_factory=list
    )

    query: str

    context_used: bool = False