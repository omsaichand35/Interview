from interviewos.models import (
    AssessmentQuestion,
    QuestionType,
    QuestionValidationResult,
    ValidationIssue,
)


class QuestionValidator:
    """
    Validate generated assessment questions.

    Structural validation is deterministic and does not use
    an LLM.
    """

    def validate(
        self,
        question: AssessmentQuestion,
    ) -> QuestionValidationResult:
        """Validate a generated question."""

        issues: list[ValidationIssue] = []

        if not question.question.strip():
            issues.append(
                ValidationIssue(
                    code="EMPTY_QUESTION",
                    message="Question text is empty.",
                )
            )

        if not question.topic.strip():
            issues.append(
                ValidationIssue(
                    code="EMPTY_TOPIC",
                    message="Question topic is empty.",
                )
            )

        if not question.explanation.strip():
            issues.append(
                ValidationIssue(
                    code="EMPTY_EXPLANATION",
                    message="Question explanation is empty.",
                )
            )

        if question.question_type in {
            QuestionType.MCQ,
            QuestionType.MULTIPLE_SELECT,
        }:
            self._validate_options(
                question,
                issues,
            )

        if question.question_type == QuestionType.TRUE_FALSE:
            self._validate_true_false(
                question,
                issues,
            )

        return QuestionValidationResult(
            valid=len(issues) == 0,
            issues=issues,
        )

    def _validate_options(
        self,
        question: AssessmentQuestion,
        issues: list[ValidationIssue],
    ) -> None:
        """Validate multiple-choice options."""

        if len(question.options) < 2:
            issues.append(
                ValidationIssue(
                    code="TOO_FEW_OPTIONS",
                    message=(
                        "Multiple-choice questions must "
                        "contain at least two options."
                    ),
                )
            )

        option_ids = [
            option.id
            for option in question.options
        ]

        if len(option_ids) != len(set(option_ids)):
            issues.append(
                ValidationIssue(
                    code="DUPLICATE_OPTION_IDS",
                    message="Option IDs must be unique.",
                )
            )

        option_texts = [
            option.text.strip().lower()
            for option in question.options
        ]

        if len(option_texts) != len(set(option_texts)):
            issues.append(
                ValidationIssue(
                    code="DUPLICATE_OPTIONS",
                    message="Options must be unique.",
                )
            )

        valid_ids = set(option_ids)

        correct_ids = set(
            question.correct_options
        )

        unknown_correct_ids = (
            correct_ids - valid_ids
        )

        if unknown_correct_ids:
            issues.append(
                ValidationIssue(
                    code="INVALID_CORRECT_OPTION",
                    message=(
                        "A correct option references "
                        "an option that does not exist."
                    ),
                )
            )

        if not correct_ids:
            issues.append(
                ValidationIssue(
                    code="NO_CORRECT_OPTION",
                    message=(
                        "At least one correct option "
                        "must be specified."
                    ),
                )
            )

        if (
            question.question_type
            == QuestionType.MCQ
            and len(correct_ids) != 1
        ):
            issues.append(
                ValidationIssue(
                    code="MCQ_MULTIPLE_CORRECT",
                    message=(
                        "An MCQ must have exactly "
                        "one correct option."
                    ),
                )
            )

    def _validate_true_false(
        self,
        question: AssessmentQuestion,
        issues: list[ValidationIssue],
    ) -> None:
        """Validate true/false questions."""

        if len(question.correct_options) != 1:
            issues.append(
                ValidationIssue(
                    code="INVALID_TRUE_FALSE_ANSWER",
                    message=(
                        "True/false questions must "
                        "have exactly one answer."
                    ),
                )
            )