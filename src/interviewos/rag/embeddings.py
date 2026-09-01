from abc import ABC, abstractmethod

from sentence_transformers import SentenceTransformer


class EmbeddingProvider(ABC):
    """Interface for embedding providers."""

    @abstractmethod
    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for text."""
        raise NotImplementedError

    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimensionality."""
        raise NotImplementedError


class SentenceTransformerEmbeddings(
    EmbeddingProvider
):
    """Embedding provider backed by Sentence Transformers."""

    def __init__(
        self,
        model_name: str,
    ) -> None:
        self.model = SentenceTransformer(
            model_name
        )

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()