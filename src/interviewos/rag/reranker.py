from abc import ABC, abstractmethod

from interviewos.models import DocumentChunk


class Reranker(ABC):
    """Interface for retrieval reranking."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: list[tuple[DocumentChunk, float]],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        raise NotImplementedError


class IdentityReranker(Reranker):
    """
    Temporary reranker that preserves retrieval order.

    This is intentionally simple until we evaluate actual
    retrieval quality and select a reranking model.
    """

    def rerank(
        self,
        query: str,
        results: list[tuple[DocumentChunk, float]],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        return results[:limit]