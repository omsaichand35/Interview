from interviewos.models import RetrievalResult


class ContextBuilder:
    """Build grounded context from retrieved documents."""

    def build(
        self,
        results: list[RetrievalResult],
    ) -> str:
        """Convert retrieval results into an LLM context block."""

        if not results:
            return ""

        sections: list[str] = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            chunk = result.chunk

            sections.append(
                "\n".join(
                    [
                        f"[SOURCE {index}]",
                        f"File: {chunk.metadata.get('filename', 'unknown')}",
                        f"Score: {result.score:.4f}",
                        "",
                        chunk.content,
                    ]
                )
            )

        return "\n\n---\n\n".join(sections)