from interviewos.models import Document, DocumentChunk


class TextChunker:
    """Split documents into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        document: Document,
    ) -> list[DocumentChunk]:
        """Split a document into overlapping chunks."""

        text = document.content.strip()

        if not text:
            return []

        chunks: list[DocumentChunk] = []

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        id=f"{document.id}:{chunk_index}",
                        document_id=document.id,
                        content=chunk_text,
                        chunk_index=chunk_index,
                        metadata={
                            "filename": document.metadata.filename,
                            "source": document.metadata.source,
                        },
                    )
                )

            if end >= len(text):
                break

            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks