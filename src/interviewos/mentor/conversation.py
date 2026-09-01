from datetime import datetime

from interviewos.models import (
    ConversationTurn,
    LearnerState,
    MessageRole,
)


class ConversationManager:
    """Manage mentor conversation history."""

    def __init__(
        self,
        state: LearnerState,
    ) -> None:
        self.state = state

    def add_user_message(
        self,
        content: str,
    ) -> None:
        """Add a user message."""

        self.state.conversation.append(
            ConversationTurn(
                role=MessageRole.USER,
                content=content,
                timestamp=datetime.now(),
            )
        )

    def add_mentor_message(
        self,
        content: str,
    ) -> None:
        """Add a mentor response."""

        self.state.conversation.append(
            ConversationTurn(
                role=MessageRole.MENTOR,
                content=content,
                timestamp=datetime.now(),
            )
        )

    def recent(
        self,
        limit: int = 10,
    ) -> list[ConversationTurn]:
        """Return the most recent conversation turns."""

        if limit <= 0:
            return []

        return self.state.conversation[-limit:]

    def format_history(
        self,
        limit: int = 10,
    ) -> str:
        """Format recent conversation for the LLM."""

        turns = self.recent(limit)

        if not turns:
            return ""

        lines: list[str] = []

        for turn in turns:
            role = turn.role.value.upper()

            lines.append(
                f"{role}: {turn.content}"
            )

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear conversation history."""

        self.state.conversation.clear()