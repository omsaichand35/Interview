import json
from pathlib import Path

from interviewos.models import QuestionBankItem


class QuestionBankStore:
    """Persist validated assessment questions."""

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
        item: QuestionBankItem,
    ) -> None:
        """Save a question-bank item."""

        path = self._path(
            item.question.id
        )

        temporary_path = path.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            item.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        temporary_path.replace(path)

    def load(
        self,
        question_id: str,
    ) -> QuestionBankItem:
        """Load a question-bank item."""

        path = self._path(
            question_id
        )

        if not path.exists():
            raise KeyError(
                f"Question '{question_id}' "
                "not found."
            )

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        return QuestionBankItem.model_validate(
            data
        )

    def exists(
        self,
        question_id: str,
    ) -> bool:
        """Check whether a question exists."""

        return self._path(
            question_id
        ).exists()

    def delete(
        self,
        question_id: str,
    ) -> None:
        """Delete a question."""

        path = self._path(
            question_id
        )

        if path.exists():
            path.unlink()

    def list_ids(self) -> list[str]:
        """Return all stored question IDs."""

        return [
            path.stem
            for path in self.directory.glob(
                "*.json"
            )
        ]

    def _path(
        self,
        question_id: str,
    ) -> Path:
        return (
            self.directory
            / f"{question_id}.json"
        )