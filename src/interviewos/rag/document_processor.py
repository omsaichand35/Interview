from pathlib import Path

from interviewos.core.exceptions import DocumentProcessingError
from interviewos.ingestion import PDFLoader, TextLoader
from interviewos.models import Document


class DocumentProcessor:
    """Convert supported knowledge files into Documents."""

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".md",
    }

    def __init__(
        self,
        pdf_loader: PDFLoader | None = None,
        text_loader: TextLoader | None = None,
    ) -> None:
        self.pdf_loader = pdf_loader or PDFLoader()
        self.text_loader = text_loader or TextLoader()

    def process(self, path: Path) -> Document:
        """Process a knowledge file."""

        path = Path(path)

        if not path.exists():
            raise DocumentProcessingError(
                f"Knowledge file does not exist: {path}"
            )

        extension = path.suffix.lower()

        if extension == ".pdf":
            return self.pdf_loader.load(path)

        if extension in {".txt", ".md"}:
            return self.text_loader.load(path)

        raise DocumentProcessingError(
            f"Unsupported knowledge file type: {extension}"
        )

    def process_directory(
        self,
        directory: Path,
    ) -> list[Document]:
        """Process all supported documents in a directory."""

        directory = Path(directory)

        if not directory.exists():
            raise DocumentProcessingError(
                f"Knowledge directory does not exist: {directory}"
            )

        if not directory.is_dir():
            raise DocumentProcessingError(
                f"Knowledge path is not a directory: {directory}"
            )

        documents: list[Document] = []

        for path in sorted(directory.rglob("*")):
            if (
                path.is_file()
                and path.suffix.lower()
                in self.SUPPORTED_EXTENSIONS
            ):
                documents.append(
                    self.process(path)
                )

        return documents