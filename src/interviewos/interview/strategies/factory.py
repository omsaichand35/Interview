from ..state import InterviewType
from ..strategy import InterviewStrategy

from .dsa import DSAInterviewStrategy
from .hr import HRInterviewStrategy
from .managerial import ManagerialInterviewStrategy
from .project import ProjectInterviewStrategy
from .technical import TechnicalInterviewStrategy


def create_strategy(
    interview_type: InterviewType,
) -> InterviewStrategy:
    """Create a strategy for an interview type."""

    strategies = {
        InterviewType.TECHNICAL:
            TechnicalInterviewStrategy,

        InterviewType.DSA:
            DSAInterviewStrategy,

        InterviewType.PROJECT:
            ProjectInterviewStrategy,

        InterviewType.HR:
            HRInterviewStrategy,

        InterviewType.MANAGERIAL:
            ManagerialInterviewStrategy,
    }

    strategy_class = strategies.get(
        interview_type
    )

    if strategy_class is None:
        raise ValueError(
            f"Unsupported interview type: "
            f"{interview_type}"
        )

    return strategy_class()  # type: ignore