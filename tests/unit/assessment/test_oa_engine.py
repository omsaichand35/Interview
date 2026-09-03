import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from interviewos.assessment.oa import OAEngine
from interviewos.models import (
    AssessmentBlueprint,
    AssessmentTopic,
    JobProfile,
    Difficulty,
    QuestionType,
    AssessmentQuestion,
    MCQOption,
    QuestionValidationResult,
)


@pytest.fixture
def mock_dependencies():
    question_generator = AsyncMock()
    evaluator = MagicMock()
    scorer = MagicMock()
    question_validator = MagicMock()
    semantic_validator = AsyncMock()
    question_bank = MagicMock()
    session_manager = MagicMock()

    # Valid question generator return
    dummy_question = AssessmentQuestion(
        id="q1",
        question="Sample Question",
        topic="Python",
        difficulty=Difficulty.MEDIUM,
        question_type=QuestionType.MCQ,
        options=[
            MCQOption(id="opt1", text="A"),
            MCQOption(id="opt2", text="B"),
            MCQOption(id="opt3", text="C"),
            MCQOption(id="opt4", text="D"),
        ],
        correct_options=["opt1"],
        explanation="Opt 1 is correct",
    )
    question_generator.generate.return_value = dummy_question
    question_validator.validate.return_value = QuestionValidationResult(valid=True, issues=[])
    semantic_validator.validate.return_value = QuestionValidationResult(valid=True, issues=[])

    return {
        "question_generator": question_generator,
        "evaluator": evaluator,
        "scorer": scorer,
        "question_validator": question_validator,
        "semantic_validator": semantic_validator,
        "question_bank": question_bank,
        "session_manager": session_manager,
    }


@pytest.mark.asyncio
async def test_oa_engine_concurrency_limit(mock_dependencies):
    active_tasks = 0
    max_active = 0

    async def mock_generate(*args, **kwargs):
        nonlocal active_tasks, max_active
        active_tasks += 1
        max_active = max(max_active, active_tasks)
        await asyncio.sleep(0.05)
        active_tasks -= 1
        return mock_dependencies["question_generator"].generate.return_value

    mock_dependencies["question_generator"].generate.side_effect = mock_generate

    engine = OAEngine(
        **mock_dependencies,
        concurrency_limit=2,
    )

    blueprint = AssessmentBlueprint(
        role="Developer",
        duration_minutes=30,
        total_questions=6,
        question_types=[QuestionType.MCQ],
        topics=[
            AssessmentTopic(name="Python", question_count=3, weight=0.5, difficulty=Difficulty.MEDIUM),
            AssessmentTopic(name="Algorithms", question_count=3, weight=0.5, difficulty=Difficulty.MEDIUM),
        ],
    )

    job = JobProfile(title="Software Engineer")

    questions = await engine.generate_questions(blueprint=blueprint, job=job)

    assert len(questions) == 6
    # Verify that concurrency limit of 2 was respected
    assert max_active <= 2
