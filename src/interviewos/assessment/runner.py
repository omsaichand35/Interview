from interviewos.models import (
    AssessmentQuestion,
    CandidateAnswer,
)

from .oa import OAEngine


class TerminalOARunner:
    """Run an objective assessment in the terminal."""

    def __init__(
        self,
        engine: OAEngine,
    ) -> None:
        self.engine = engine

    def run(
        self,
        session_id: str,
    ):
        """Run an existing assessment session."""

        session = self.engine.session_manager.start(
            session_id
        )

        print()
        print("=" * 70)
        print("INTERVIEWOS OBJECTIVE ASSESSMENT")
        print("=" * 70)

        print(f"\nRole: {session.role}")
        print(
            f"Questions: "
            f"{len(session.question_ids)}"
        )

        input(
            "\nPress ENTER to begin..."
        )

        for index, question_id in enumerate(
            session.question_ids,
            start=1,
        ):
            question = (
                self.engine.question_bank.get(
                    question_id
                )
            )

            if question is None:
                raise RuntimeError(
                    f"Question '{question_id}' "
                    "not found."
                )

            mapping = self._display_question(
                question,
                index,
                len(session.question_ids),
            )

            answer = self._collect_answer(
                question,
                mapping
            )

            self.engine.session_manager.answer(
                session_id,
                answer,
            )

        print()
        print("=" * 70)
        print("SUBMITTING ASSESSMENT")
        print("=" * 70)

        self.engine.session_manager.submit(
            session_id
        )

        result = (
            self.engine.evaluate_session(
                session_id
            )
        )

        self._display_result(
            result
        )

        return result

    def _display_question(
        self,
        question: AssessmentQuestion,
        number: int,
        total: int,
    ) -> dict[str, str]:
        """Display one question and return option mapping."""
        import string
        letters = string.ascii_lowercase

        print()
        print("-" * 70)
        print(
            f"Question {number}/{total}"
        )
        print("-" * 70)

        print()
        print(question.question)

        print()

        mapping = {}
        for i, option in enumerate(question.options):
            letter = letters[i]
            mapping[letter.upper()] = option.id
            print(
                f"  {letter}. "
                f"{option.text}"
            )

        print()
        return mapping

    def _collect_answer(
        self,
        question: AssessmentQuestion,
        mapping: dict[str, str],
    ) -> CandidateAnswer:
        """Collect an answer from the candidate."""

        while True:
            raw = input(
                "Answer: "
            ).strip()

            if not raw:
                print(
                    "Please provide an answer."
                )
                continue

            selected = [
                value.strip().upper()
                for value in raw.split(",")
                if value.strip()
            ]

            valid_letters = set(mapping.keys())

            if not all(
                value in valid_letters
                for value in selected
            ):
                print(
                    "Invalid option. "
                    "Choose from: "
                    + ", ".join(
                        sorted(valid_letters)
                    )
                )
                continue
                
            selected_ids = [mapping[letter] for letter in selected]

            return CandidateAnswer(
                question_id=question.id,
                selected_options=selected_ids,
            )

    def _display_result(
            self,
            result,
    ) -> None:
        """Display the final assessment result."""

        print()
        print("=" * 70)
        print("ASSESSMENT COMPLETE")
        print("=" * 70)

        print(
            f"\nCorrect: "
            f"{result.correct_answers}/"
            f"{result.total_questions}"
        )

        print(
            f"Score: "
            f"{result.score * 100:.1f}%"
        )

        print(
            f"Status: "
            f"{'PASSED' if result.passed else 'NOT PASSED'}"
        )

        if result.topic_scores:

            print("\nTopic Performance:")
            print()

            for topic_score in result.topic_scores:
                print(
                    f"  {topic_score.topic}: "
                    f"{topic_score.score * 100:.1f}% "
                    f"("
                    f"{topic_score.correct_answers}/"
                    f"{topic_score.total_questions}"
                    f")"
                )

        print()