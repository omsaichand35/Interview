from collections import defaultdict

from interviewos.models import (
    AssessmentQuestion,
    AssessmentResult,
    QuestionEvaluation,
    TopicScore,
)


class AssessmentScorer:
    """Calculate objective assessment scores."""

    def score(
        self,
        questions: list[AssessmentQuestion],
        evaluations: list[QuestionEvaluation],
        threshold: float = 0.6,
    ) -> AssessmentResult:
        """Calculate overall and topic-level scores."""

        if not evaluations:
            raise ValueError(
                "Cannot score an empty assessment."
            )

        question_map = {
            question.id: question
            for question in questions
        }

        correct = sum(
            1
            for evaluation in evaluations
            if evaluation.correct
        )

        total = len(evaluations)

        overall_score = correct / total

        topic_results = defaultdict(
            list
        )

        for evaluation in evaluations:
            question = question_map.get(
                evaluation.question_id
            )

            if question is None:
                continue

            topic_results[
                question.topic
            ].append(evaluation)

        topic_scores: list[TopicScore] = []

        for topic, topic_evaluations in (
            topic_results.items()
        ):
            topic_total = len(
                topic_evaluations
            )

            topic_correct = sum(
                1
                for evaluation
                in topic_evaluations
                if evaluation.correct
            )

            topic_score = (
                topic_correct
                / topic_total
            )

            topic_scores.append(
                TopicScore(
                    topic=topic,
                    total_questions=topic_total,
                    correct_answers=topic_correct,
                    score=topic_score,
                )
            )

        return AssessmentResult(
            total_questions=total,
            correct_answers=correct,
            score=overall_score,
            topic_scores=topic_scores,
            question_results=evaluations,
            passed=overall_score >= threshold,
        )