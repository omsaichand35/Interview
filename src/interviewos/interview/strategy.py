from abc import ABC, abstractmethod

from interviewos.models import JobProfile


class InterviewStrategy(ABC):
    """Base strategy for a type of interview."""

    @abstractmethod
    def build_context(
        self,
        job: JobProfile,
    ) -> str:
        """Build the interview context."""

        raise NotImplementedError

    @abstractmethod
    def competencies(self) -> list[str]:
        """Return competencies being evaluated."""

        raise NotImplementedError