import asyncio

from interviewos.models import (
    AssessmentBlueprint,
    AssessmentQuestion,
    CandidateAnswer,
    JobProfile,
    QuestionEvaluation,
    QuestionType, AssessmentSession, AssessmentSessionStatus,
)

from .evaluator import AssessmentEvaluator
from .question_bank import QuestionBank
from .question_generator import QuestionGenerator
from .scoring import AssessmentScorer

from .question_validator import QuestionValidator
from .semantic_validation import SemanticQuestionValidator
from .session import AssessmentSessionManager

class OAEngine:
    """Run an objective assessment."""

    def __init__(
            self,
            question_generator: QuestionGenerator,
            evaluator: AssessmentEvaluator,
            scorer: AssessmentScorer,
            question_validator: QuestionValidator,
            semantic_validator: SemanticQuestionValidator,
            question_bank: QuestionBank,
            session_manager: AssessmentSessionManager,
    ) -> None:

        self.question_generator = question_generator
        self.evaluator = evaluator
        self.scorer = scorer
        self.question_validator = question_validator
        self.semantic_validator = semantic_validator
        self.question_bank = question_bank
        self.session_manager = session_manager
    async def _generate_single_question(
            self,
            topic,
            job: JobProfile,
            question_type: QuestionType,
            max_attempts: int,
    ) -> AssessmentQuestion:
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            question = await self.question_generator.generate(
                topic=topic,
                job=job,
                question_type=question_type,
            )
            structural_result = self.question_validator.validate(question)
            if not structural_result.valid:
                continue

            semantic_result = await self.semantic_validator.validate(
                question=question,
                job=job,
            )
            if not semantic_result.valid:
                continue

            self.question_bank.add(
                question=question,
                source="llm_generated",
            )
            return question

        raise RuntimeError(
            f"Could not generate a valid question "
            f"for topic '{topic.name}' after "
            f"{max_attempts} attempts."
        )

    async def generate_questions(
            self,
            blueprint: AssessmentBlueprint,
            job: JobProfile,
            max_attempts: int = 3,
    ) -> list[AssessmentQuestion]:
        """Generate validated assessment questions."""

        question_types = blueprint.question_types

        if not question_types:
            question_types = [
                QuestionType.MCQ
            ]

        type_index = 0
        tasks = []

        for topic in blueprint.topics:
            for _ in range(topic.question_count):
                question_type = question_types[
                    type_index % len(question_types)
                ]
                tasks.append(
                    self._generate_single_question(
                        topic=topic,
                        job=job,
                        question_type=question_type,
                        max_attempts=max_attempts,
                    )
                )
                type_index += 1

        questions = await asyncio.gather(*tasks)
        return list(questions)

    def evaluate(
        self,
        questions: list[AssessmentQuestion],
        answers: list[CandidateAnswer],
        threshold: float = 0.6,
    ):
        """Evaluate an assessment."""

        answer_map = {
            answer.question_id: answer
            for answer in answers
        }

        evaluations: list[
            QuestionEvaluation
        ] = []

        for question in questions:

            answer = answer_map.get(
                question.id
            )

            if answer is None:
                answer = CandidateAnswer(
                    question_id=question.id
                )

            evaluation = (
                self.evaluator.evaluate(
                    question=question,
                    answer=answer,
                )
            )

            evaluations.append(
                evaluation
            )

        return self.scorer.score(
            evaluations=evaluations,
            threshold=threshold,
        )

    async def create_session(
            self,
            blueprint: AssessmentBlueprint,
            job: JobProfile,
            candidate_id: str,
    ) -> AssessmentSession:
        """Create an assessment session from a blueprint."""

        questions = await self.generate_questions(
            blueprint=blueprint,
            job=job,
        )

        session = self.session_manager.create(
            candidate_id=candidate_id,
            role=job.title,
            questions=questions,
            duration_minutes=blueprint.duration_minutes,
        )

        return session

    def evaluate_session(
            self,
            session_id: str,
            threshold: float = 0.6,
    ):
        """Evaluate a submitted assessment."""

        session = self.session_manager.get(
            session_id
        )

        if (
                session.status
                != AssessmentSessionStatus.SUBMITTED
        ):
            raise ValueError(
                "Assessment must be submitted before evaluation."
            )

        evaluations = []

        answer_map = {
            answer.question_id: answer
            for answer in session.answers
        }

        for question_id in session.question_ids:

            question = self.question_bank.get(
                question_id
            )

            if question is None:
                raise RuntimeError(
                    f"Question '{question_id}' "
                    "is missing from the question bank."
                )

            answer = answer_map.get(
                question_id
            )

            if answer is None:
                answer = CandidateAnswer(
                    question_id=question_id
                )

            evaluation = self.evaluator.evaluate(
                question=question,
                answer=answer,
            )

            evaluations.append(
                evaluation
            )

        questions = []

        for question_id in session.question_ids:
            question = self.question_bank.get(
                question_id
            )

            if question is None:
                raise RuntimeError(
                    f"Question '{question_id}' "
                    "is missing from the question bank."
                )

            questions.append(question)

        result = self.scorer.score(
            questions=questions,
            evaluations=evaluations,
            threshold=threshold,
        )

        session.result = result

        session.status = (
            AssessmentSessionStatus.EVALUATED
        )

        return result

