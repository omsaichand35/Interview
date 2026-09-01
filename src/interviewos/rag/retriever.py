from .embeddings import EmbeddingProvider
from .vector_store import VectorStore
from interviewos.models import DocumentChunk


class Retriever:
    """Retrieve relevant knowledge chunks."""

    def __init__(
        self,
        embeddings: EmbeddingProvider,
        vector_store: VectorStore,
    ) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        """Retrieve the most relevant chunks."""

        if not query.strip():
            return []

        query_vector = self.embeddings.embed(
            [query]
        )[0]

        return self.vector_store.search(
            vector=query_vector,
            limit=limit,
        )