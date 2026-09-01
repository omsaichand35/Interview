from uuid import uuid4

from interviewos.models import Candidate

from .candidate_store import CandidateStore


class CandidateManager:
    """Create and retrieve candidates."""

    def __init__(
        self,
        store: CandidateStore,
    ) -> None:
        self.store = store

    def create(
        self,
        name: str,
        email: str,
        metadata: dict[str, str] | None = None,
    ) -> Candidate:
        """Create a candidate."""

        if not name.strip():
            raise ValueError(
                "Candidate name cannot be empty."
            )

        if not email.strip():
            raise ValueError(
                "Candidate email cannot be empty."
            )

        candidate = Candidate(
            id=str(uuid4()),
            name=name.strip(),
            email=email.strip(),
            metadata=metadata or {},
        )

        self.store.save(
            candidate
        )

        return candidate

    def get(
        self,
        candidate_id: str,
    ) -> Candidate:
        """Retrieve a candidate."""

        return self.store.load(
            candidate_id
        )