from pathlib import PurePosixPath

from .repository import (
    RepositoryFile,
    is_relevant_file,
)


IMPORTANT_FILE_NAMES = {
    "readme.md",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "makefile",
}


IMPORTANT_DIRECTORY_NAMES = {
    "src",
    "app",
    "lib",
    "core",
    "services",
    "models",
    "api",
    "tests",
}


class RepositoryFileSelector:
    """Select files most useful for project analysis."""

    def select(
        self,
        files: list[RepositoryFile],
        limit: int = 30,
    ) -> list[RepositoryFile]:
        """Select the most relevant repository files."""

        relevant = [
            file
            for file in files
            if is_relevant_file(file.path)
        ]

        ranked = sorted(
            relevant,
            key=self._priority,
            reverse=True,
        )

        return ranked[:limit]

    def _priority(
        self,
        file: RepositoryFile,
    ) -> int:
        """Calculate file relevance."""

        path = PurePosixPath(
            file.path
        )

        name = path.name.lower()

        score = 0

        if name in IMPORTANT_FILE_NAMES:
            score += 100

        if any(
            directory in IMPORTANT_DIRECTORY_NAMES
            for directory in path.parts
        ):
            score += 30

        if name.startswith("test"):
            score += 10

        if path.suffix.lower() in {
            ".py",
            ".java",
            ".kt",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".cpp",
        }:
            score += 20

        # Extremely large files are less useful
        # for initial analysis.
        if file.size > 500_000:
            score -= 50

        return score