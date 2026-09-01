from datetime import datetime

from interviewos.assessment.question_bank_store import QuestionBankStore
from interviewos.models import (
    AssessmentQuestion,
    QuestionBankItem,
)


class QuestionBank:
    """
    In-memory question bank.

    Persistence will be added later.
    """

    def __init__(
            self,
            store: QuestionBankStore,
    ) -> None:

        self.store = store

        self._questions: dict[
            str,
            QuestionBankItem,
        ] = {}

    def add(
            self,
            question: AssessmentQuestion,
            source: str = "llm_generated",
            quality_score: float = 1.0,
    ) -> QuestionBankItem:
        """Add and persist a validated question."""

        item = QuestionBankItem(
            question=question,
            created_at=datetime.now(),
            source=source,
            quality_score=quality_score,
        )

        self._questions[
            question.id
        ] = item

        self.store.save(item)

        return item

    def get(
            self,
            question_id: str,
    ) -> AssessmentQuestion | None:
        """Retrieve a question from memory or disk."""

        item = self._questions.get(
            question_id
        )

        if item is not None:
            return item.question

        if not self.store.exists(
                question_id
        ):
            return None

        item = self.store.load(
            question_id
        )

        self._questions[
            question_id
        ] = item

        return item.question

    def get_item(
            self,
            question_id: str,
    ) -> QuestionBankItem | None:
        """Retrieve a complete question-bank item."""

        item = self._questions.get(
            question_id
        )

        if item is not None:
            return item

        if not self.store.exists(
                question_id
        ):
            return None

        item = self.store.load(
            question_id
        )

        self._questions[
            question_id
        ] = item

        return item

    def all(self) -> list[QuestionBankItem]:
        """Return all questions."""

        return list(
            self._questions.values()
        )

    def mark_used(
            self,
            question_id: str,
    ) -> None:
        """Increment and persist question usage."""

        item = self.get_item(
            question_id
        )

        if item is None:
            raise KeyError(
                f"Question '{question_id}' "
                "does not exist."
            )

        item.times_used += 1

        self._questions[
            question_id
        ] = item

        self.store.save(item)

    def count(self) -> int:
        """Return number of stored questions."""

        return len(self._questions)

    def select(
            self,
            topic: str | None = None,
            difficulty: str | None = None,
            question_type: str | None = None,
            limit: int = 1,
    ) -> list[AssessmentQuestion]:
        """Select questions matching the requested criteria."""

        candidates = self.all()

        if topic:
            candidates = [
                item
                for item in candidates
                if item.question.topic.lower()
                   == topic.lower()
            ]

        if difficulty:
            candidates = [
                item
                for item in candidates
                if item.question.difficulty.value
                   == difficulty
            ]

        if question_type:
            candidates = [
                item
                for item in candidates
                if item.question.question_type.value
                   == question_type
            ]

        candidates.sort(
            key=lambda item: (
                item.times_used,
                -item.quality_score,
            )
        )

        selected = candidates[:limit]

        for item in selected:
            self.mark_used(
                item.question.id
            )

        return [
            item.question
            for item in selected
        ]

    def load_all(
            self,
    ) -> int:
        """Load all persisted questions into memory."""

        loaded = 0

        for question_id in self.store.list_ids():

            if question_id in self._questions:
                continue

            item = self.store.load(
                question_id
            )

            self._questions[
                question_id
            ] = item

            loaded += 1

        return loaded