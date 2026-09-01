from pathlib import Path


class ProjectPaths:
    """
    Centralized filesystem paths for InterviewOS.

    All paths are resolved relative to the project root.
    """

    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            root = self._find_project_root()

        self.root = root.resolve()

        # Main directories
        self.src = self.root / "src"
        self.data = self.root / "data"
        self.outputs = self.root / "outputs"

        # Input data
        self.input = self.data / "input"
        self.resumes = self.input / "resumes"
        self.job_descriptions = self.input / "job_descriptions"

        # Knowledge base
        self.knowledge = self.data / "knowledge"
        self.books = self.knowledge / "books"
        self.documentation = self.knowledge / "documentation"
        self.notes = self.knowledge / "notes"
        self.custom_knowledge = self.knowledge / "custom"

        # Processed data
        self.processed = self.data / "processed"
        self.processed_resumes = self.processed / "resumes"
        self.processed_job_descriptions = self.processed / "job_descriptions"
        self.processed_knowledge = self.processed / "knowledge"

        # Vector store
        self.vectorstore = self.data / "vectorstore"

        # Outputs
        self.analyses = self.outputs / "analyses"
        self.plans = self.outputs / "plans"
        self.sessions = self.outputs / "sessions"
        self.question_bank = self.data / "question_bank"
        self.candidates = self.data / "candidates"

    @staticmethod
    def _find_project_root() -> Path:
        """
        Find the InterviewOS project root.

        Starting from this file, walk upward until pyproject.toml
        is found.
        """
        current = Path(__file__).resolve()

        for parent in current.parents:
            if (parent / "pyproject.toml").exists():
                return parent

        raise RuntimeError(
            "Could not locate InterviewOS project root. "
            "Expected pyproject.toml in a parent directory."
        )

    def create_directories(self) -> None:
        """Create all runtime data and output directories."""
        directories = [
            self.resumes,
            self.job_descriptions,
            self.books,
            self.documentation,
            self.notes,
            self.custom_knowledge,
            self.processed_resumes,
            self.processed_job_descriptions,
            self.processed_knowledge,
            self.vectorstore,
            self.analyses,
            self.plans,
            self.sessions,
            self.question_bank,
            self.candidates
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


def get_project_paths() -> ProjectPaths:
    """Return the project's centralized path configuration."""
    return ProjectPaths()