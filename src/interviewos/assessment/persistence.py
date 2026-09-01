import json
from pathlib import Path

from interviewos.models import AssessmentSession


class AssessmentSessionStore:
    """Persist assessment sessions as JSON files."""

    def __init__(
        self,
        directory: Path,
    ) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        session: AssessmentSession,
    ) -> None:
        """Save an assessment session."""

        path = self._path(session.id)

        temporary_path = path.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            session.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        temporary_path.replace(path)

    def load(
        self,
        session_id: str,
    ) -> AssessmentSession:
        """Load a session from disk."""

        path = self._path(session_id)

        if not path.exists():
            raise KeyError(
                f"Assessment session "
                f"'{session_id}' not found."
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return AssessmentSession.model_validate(
            data
        )

    def exists(
        self,
        session_id: str,
    ) -> bool:
        """Check whether a session exists."""

        return self._path(
            session_id
        ).exists()

    def delete(
        self,
        session_id: str,
    ) -> None:
        """Delete a persisted session."""

        path = self._path(
            session_id
        )

        if path.exists():
            path.unlink()

    def _path(
        self,
        session_id: str,
    ) -> Path:
        """Return the storage path."""

        return (
            self.directory
            / f"{session_id}.json"
        )