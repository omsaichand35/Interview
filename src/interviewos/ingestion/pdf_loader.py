from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from interviewos.core.exceptions import DocumentProcessingError
from interviewos.models.documents import Document, DocumentMetadata

from .document_loader import DocumentLoader
from .text_cleaner import TextCleaner


class PDFLoader(DocumentLoader):
    """Load and extract text from PDF documents."""

    def __init__(self, cleaner: TextCleaner | None = None) -> None:
        self.cleaner = cleaner or TextCleaner()

    def load(self, path: Path) -> Document:
        """
        Extract text from a PDF and return a normalized Document.
        """

        path = Path(path)

        if not path.exists():
            raise DocumentProcessingError(
                f"PDF file does not exist: {path}"
            )

        if not path.is_file():
            raise DocumentProcessingError(
                f"Path is not a file: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise DocumentProcessingError(
                f"Expected a PDF file, received: {path.suffix}"
            )

        try:
            reader = PdfReader(str(path))

            pages: list[str] = []

            for page in reader.pages:
                page_text = page.extract_text() or ""

                if page_text.strip():
                    pages.append(page_text)

            raw_text = "\n\n".join(pages)
            cleaned_text = self.cleaner.clean(raw_text)

        except Exception as exc:
            raise DocumentProcessingError(
                f"Failed to process PDF: {path}"
            ) from exc

        if not cleaned_text:
            raise DocumentProcessingError(
                f"No extractable text found in PDF: {path}"
            )

        metadata = DocumentMetadata(
            source="pdf",
            filename=path.name,
            file_type="application/pdf",
            path=path.resolve(),
        )

        return Document(
            id=str(uuid4()),
            content=cleaned_text,
            metadata=metadata,
        )