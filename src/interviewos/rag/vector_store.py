from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from interviewos.models import DocumentChunk


class VectorStore(ABC):
    """Interface for vector storage."""

    @abstractmethod
    def create_collection(
        self,
        dimension: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def add(
        self,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        raise NotImplementedError


class QdrantVectorStore(VectorStore):
    """Persistent local Qdrant vector store."""

    def __init__(
        self,
        path: Path,
        collection_name: str = "interviewos_knowledge",
    ) -> None:
        self.path = Path(path)
        self.collection_name = collection_name

        self.path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = QdrantClient(
            path=str(self.path)
        )

    def create_collection(
        self,
        dimension: int,
    ) -> None:

        collections = self.client.get_collections()

        existing = {
            collection.name
            for collection in collections.collections
        }

        if self.collection_name in existing:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=Distance.COSINE,
            ),
        )

    def add(
        self,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> None:

        if len(chunks) != len(vectors):
            raise ValueError(
                "Number of chunks must match number of vectors."
            )

        points: list[PointStruct] = []

        for chunk, vector in zip(
            chunks,
            vectors,
            strict=True,
        ):
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "chunk_id": chunk.id,
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "metadata": chunk.metadata,
                    },
                )
            )

        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
        ).points

        chunks: list[tuple[DocumentChunk, float]] = []

        for result in results:
            payload = result.payload or {}

            chunk = DocumentChunk(
                id=str(payload["chunk_id"]),
                document_id=str(
                    payload["document_id"]
                ),
                content=str(payload["content"]),
                chunk_index=int(
                    payload["chunk_index"]
                ),
                metadata=payload.get(
                    "metadata",
                    {},
                ),
            )

            chunks.append(
                (chunk, float(result.score))
            )

        return chunks