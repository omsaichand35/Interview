from abc import ABC, abstractmethod
from pathlib import Path

from interviewos.models.documents import Document


class DocumentLoader(ABC):
    """Base interface for document loaders."""

    @abstractmethod
    def load(self, path: Path) -> Document:
        """
        Load a file and convert it into a normalized Document.

        Args:
            path: Path to the source file.

        Returns:
            Normalized Document.
        """
        raise NotImplementedError