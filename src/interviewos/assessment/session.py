from datetime import datetime
from uuid import uuid4

from interviewos.models import (
    AssessmentQuestion,
    AssessmentSession,
    AssessmentSessionStatus,
    CandidateAnswer,
)
from .persistence import AssessmentSessionStore

from .question_bank import QuestionBank

from datetime import datetime, timedelta

from .clock import Clock


class AssessmentSessionManager:
    """Manage candidate assessment sessions."""

    def __init__(
            self,
            question_bank: QuestionBank,
            store: AssessmentSessionStore,
            clock: Clock | None = None,
    ) -> None:

        self.question_bank = question_bank
        self.store = store
        self.clock = clock or Clock()

        self._sessions: dict[
            str,
            AssessmentSession,
        ] = {}

    def create(
            self,
            candidate_id: str,
            role: str,
            questions: list[AssessmentQuestion],
            duration_minutes: int,
    ) -> AssessmentSession:
        """Create a new assessment session."""

        if not questions:
            raise ValueError(
                "Cannot create an empty assessment."
            )

        session = AssessmentSession(
            id=str(uuid4()),
            candidate_id=candidate_id,
            role=role,
            assessment_id=str(uuid4()),
            question_ids=[
                question.id
                for question in questions
            ],
            duration_minutes=duration_minutes,
        )

        self._sessions[session.id] = session

        self.store.save(session)

        return session

    def start(
        self,
        session_id: str,
    ) -> AssessmentSession:
        """Start an assessment."""

        session = self.get(
            session_id
        )

        if (
            session.status
            != AssessmentSessionStatus.CREATED
        ):
            raise ValueError(
                "Assessment has already been started."
            )

        session.status = (
            AssessmentSessionStatus.IN_PROGRESS
        )

        session.started_at = datetime.now()

        self.store.save(session)

        return session

    def answer(
            self,
            session_id: str,
            answer: CandidateAnswer,
    ) -> None:
        """Record one candidate answer."""

        session = self.get(
            session_id
        )

        if (
                session.status
                != AssessmentSessionStatus.IN_PROGRESS
        ):
            raise ValueError(
                "Assessment is not currently active."
            )

        if self.is_expired(
                session_id
        ):
            self.submit(
                session_id
            )

            raise TimeoutError(
                "Assessment time has expired."
            )

        if answer.question_id not in session.question_ids:
            raise ValueError(
                "Question does not belong to this session."
            )

        existing_index = next(
            (
                index
                for index, existing in enumerate(
                    session.answers
                )
                if existing.question_id
                == answer.question_id
            ),
            None,
        )

        if existing_index is not None:
            session.answers[
                existing_index
            ] = answer
        else:
            session.answers.append(
                answer
            )
        self.store.save(session)

    def submit(
        self,
        session_id: str,
    ) -> AssessmentSession:
        """Submit an assessment."""

        session = self.get(
            session_id
        )

        if (
            session.status
            != AssessmentSessionStatus.IN_PROGRESS
        ):
            raise ValueError(
                "Assessment is not currently active."
            )

        session.status = (
            AssessmentSessionStatus.SUBMITTED
        )

        session.submitted_at = datetime.now()

        self.store.save(session)

        return session

    def get(
            self,
            session_id: str,
    ) -> AssessmentSession:

        session = self._sessions.get(
            session_id
        )

        if session is not None:
            return session

        if self.store.exists(
                session_id
        ):
            session = self.store.load(
                session_id
            )

            self._sessions[
                session_id
            ] = session

            return session

        raise KeyError(
            f"Assessment session "
            f"'{session_id}' not found."
        )

    def get_deadline(
            self,
            session_id: str,
    ) -> datetime:
        """Return the authoritative assessment deadline."""

        session = self.get(
            session_id
        )

        if session.started_at is None:
            raise ValueError(
                "Assessment has not started."
            )

        return (
                session.started_at
                + timedelta(
            minutes=session.duration_minutes
        )
        )

    def get_remaining_seconds(
            self,
            session_id: str,
    ) -> int:
        """Return remaining assessment time."""

        session = self.get(
            session_id
        )

        if session.started_at is None:
            return (
                    session.duration_minutes
                    * 60
            )

        deadline = self.get_deadline(
            session_id
        )

        remaining = (
                deadline
                - self.clock.now()
        ).total_seconds()

        return max(
            0,
            int(remaining),
        )

    def is_expired(
            self,
            session_id: str,
    ) -> bool:
        """Determine whether the assessment has expired."""

        session = self.get(
            session_id
        )

        if session.status != AssessmentSessionStatus.IN_PROGRESS:
            return False

        return (
                self.get_remaining_seconds(
                    session_id
                )
                <= 0
        )

    def enforce_timeout(
            self,
            session_id: str,
    ) -> bool:
        """
        Submit an assessment if its time has expired.

        Returns True when the session was automatically
        submitted.
        """

        if not self.is_expired(
                session_id
        ):
            return False

        self.submit(
            session_id
        )

        return True