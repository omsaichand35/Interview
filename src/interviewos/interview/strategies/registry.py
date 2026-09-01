from ..state import InterviewType
from ..strategy import InterviewStrategy

from .factory import create_strategy


class StrategyRegistry:
    """Provide interview strategies."""

    def get(
        self,
        interview_type: InterviewType,
    ) -> InterviewStrategy:
        """Return the appropriate strategy."""

        return create_strategy(
            interview_type
        )