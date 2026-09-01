LEVELS = [
    "easy",
    "medium",
    "hard",
]


def increase_difficulty(
    current: str,
) -> str:
    """Increase interview difficulty."""

    if current not in LEVELS:
        return "medium"

    index = LEVELS.index(current)

    return LEVELS[
        min(index + 1, len(LEVELS) - 1)
    ]


def decrease_difficulty(
    current: str,
) -> str:
    """Decrease interview difficulty."""

    if current not in LEVELS:
        return "medium"

    index = LEVELS.index(current)

    return LEVELS[
        max(index - 1, 0)
    ]