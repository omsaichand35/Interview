import json
from pathlib import Path

from interviewos.models import Candidate


class CandidateStore:
    """Persist candidate records."""

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
        candidate: Candidate,
    ) -> None:
        """Save a candidate."""

        path = self._path(
            candidate.id
        )

        temporary_path = path.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            candidate.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        temporary_path.replace(path)

    def load(
        self,
        candidate_id: str,
    ) -> Candidate:
        """Load a candidate."""

        path = self._path(
            candidate_id
        )

        if not path.exists():
            raise KeyError(
                f"Candidate '{candidate_id}' "
                "not found."
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return Candidate.model_validate(
            data
        )

    def exists(
        self,
        candidate_id: str,
    ) -> bool:
        """Check whether candidate exists."""

        return self._path(
            candidate_id
        ).exists()

    def _path(
        self,
        candidate_id: str,
    ) -> Path:
        return (
            self.directory
            / f"{candidate_id}.json"
        )