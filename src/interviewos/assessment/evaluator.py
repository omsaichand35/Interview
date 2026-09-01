from interviewos.models import (
    AssessmentQuestion,
    CandidateAnswer,
    QuestionEvaluation,
)


class AssessmentEvaluator:
    """Evaluate objective assessment answers."""

    def evaluate(
        self,
        question: AssessmentQuestion,
        answer: CandidateAnswer,
    ) -> QuestionEvaluation:
        """Evaluate one candidate answer."""

        expected = set(
            question.correct_options
        )

        selected = set(
            answer.selected_options
        )

        correct = (
            selected == expected
        )

        return QuestionEvaluation(
            question_id=question.id,
            correct=correct,
            score=1.0 if correct else 0.0,
            feedback=(
                "Correct."
                if correct
                else "Incorrect."
            ),
        )