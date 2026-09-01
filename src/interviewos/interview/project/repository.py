from pydantic import BaseModel, Field
from pathlib import PurePosixPath

SUPPORTED_SOURCE_EXTENSIONS = {
    ".py",
    ".java",
    ".kt",
    ".kts",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".cpp",
    ".cc",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".swift",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".xml",
    ".md",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "target",
    "coverage",
    "checkpoints",
    "datasets",
    "data",
}


class RepositoryFile(BaseModel):
    """A file discovered in a repository."""

    path: str

    size: int = 0

    content: str | None = None


class RepositorySnapshot(BaseModel):
    """A point-in-time representation of a repository."""

    url: str

    owner: str

    name: str

    description: str | None = None

    default_branch: str = "main"

    languages: dict[str, int] = Field(
        default_factory=dict,
    )

    files: list[RepositoryFile] = Field(
        default_factory=list,
    )

    readme: str | None = None

    dependencies: list[str] = Field(
        default_factory=list,
    )

    commits: list[str] = Field(
        default_factory=list,
    )

def is_relevant_file(
        path: str,
) -> bool:
    """Determine whether a repository file is relevant."""

    pure_path = PurePosixPath(path)

    if any(
            part in IGNORED_DIRECTORIES
            for part in pure_path.parts
    ):
        return False

    suffix = pure_path.suffix.lower()

    return (
            suffix
            in SUPPORTED_SOURCE_EXTENSIONS
    )