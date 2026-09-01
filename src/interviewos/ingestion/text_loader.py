from pathlib import Path
from uuid import uuid4

from interviewos.core.exceptions import DocumentProcessingError
from interviewos.models.documents import Document, DocumentMetadata

from .document_loader import DocumentLoader
from .text_cleaner import TextCleaner


class TextLoader(DocumentLoader):
    """Load plain-text documents."""

    def __init__(self, cleaner: TextCleaner | None = None) -> None:
        self.cleaner = cleaner or TextCleaner()

    def load(self, path: Path) -> Document:
        """Read and normalize a text file."""

        path = Path(path)

        if not path.exists():
            raise DocumentProcessingError(
                f"Text file does not exist: {path}"
            )

        if not path.is_file():
            raise DocumentProcessingError(
                f"Path is not a file: {path}"
            )

        try:
            raw_text = path.read_text(encoding="utf-8")
            cleaned_text = self.cleaner.clean(raw_text)

        except UnicodeDecodeError as exc:
            raise DocumentProcessingError(
                f"Could not decode text file as UTF-8: {path}"
            ) from exc

        except OSError as exc:
            raise DocumentProcessingError(
                f"Could not read text file: {path}"
            ) from exc

        if not cleaned_text:
            raise DocumentProcessingError(
                f"Text file is empty: {path}"
            )

        metadata = DocumentMetadata(
            source="text",
            filename=path.name,
            file_type="text/plain",
            path=path.resolve(),
        )

        return Document(
            id=str(uuid4()),
            content=cleaned_text,
            metadata=metadata,
        )