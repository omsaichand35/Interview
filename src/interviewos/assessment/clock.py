from datetime import datetime


class Clock:
    """Provide the current time."""

    def now(self) -> datetime:
        return datetime.now()