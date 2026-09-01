import re


class TextCleaner:
    """Clean and normalize extracted document text."""

    def clean(self, text: str) -> str:
        """
        Normalize extracted text.

        The cleaner intentionally performs conservative transformations
        so that meaningful document structure is not destroyed.
        """

        if not text:
            return ""

        # Normalize line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove excessive spaces while preserving newlines.
        text = re.sub(r"[ \t]+", " ", text)

        # Collapse excessive blank lines.
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove whitespace around lines.
        lines = [line.strip() for line in text.split("\n")]

        text = "\n".join(lines)

        # Final cleanup.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()