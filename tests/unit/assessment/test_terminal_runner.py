import pytest
from unittest.mock import MagicMock, patch

from interviewos.assessment.runner import TerminalOARunner
from interviewos.models import AssessmentQuestion, MCQOption, Difficulty, QuestionType, AssessmentSessionStatus


@pytest.fixture
def mock_question():
    return AssessmentQuestion(
        id="q101",
        question="What is the time complexity of binary search?",
        topic="Algorithms",
        difficulty=Difficulty.EASY,
        question_type=QuestionType.MCQ,
        options=[
            MCQOption(id="opt_a", text="O(N)"),
            MCQOption(id="opt_b", text="O(log N)"),
            MCQOption(id="opt_c", text="O(N^2)"),
            MCQOption(id="opt_d", text="O(1)"),
        ],
        correct_options=["opt_b"],
        explanation="Binary search repeatedly halves the search space.",
    )


def test_collect_answer_valid_choice(mock_question):
    engine = MagicMock()
    runner = TerminalOARunner(engine)
    mapping = {"A": "opt_a", "B": "opt_b", "C": "opt_c", "D": "opt_d"}

    with patch("rich.prompt.Prompt.ask", side_effect=["b"]):
        answer = runner._collect_answer(mock_question, mapping)
        assert answer is not None
        assert answer.question_id == "q101"
        assert answer.selected_options == ["opt_b"]


def test_collect_answer_invalid_then_valid_choice(mock_question):
    engine = MagicMock()
    runner = TerminalOARunner(engine)
    mapping = {"A": "opt_a", "B": "opt_b", "C": "opt_c", "D": "opt_d"}

    # User enters "Z" (invalid), then "A B" (multiple), then "A" (valid)
    with patch("rich.prompt.Prompt.ask", side_effect=["Z", "A B", "a"]):
        answer = runner._collect_answer(mock_question, mapping)
        assert answer is not None
        assert answer.selected_options == ["opt_a"]


def test_collect_answer_exit_command(mock_question):
    engine = MagicMock()
    runner = TerminalOARunner(engine)
    mapping = {"A": "opt_a", "B": "opt_b"}

    with patch("rich.prompt.Prompt.ask", side_effect=["done"]):
        answer = runner._collect_answer(mock_question, mapping)
        assert answer is None


def test_runner_handles_timeout_gracefully(mock_question):
    engine = MagicMock()
    mock_session = MagicMock()
    mock_session.role = "Software Engineer"
    mock_session.question_ids = ["q101"]
    mock_session.status = AssessmentSessionStatus.SUBMITTED

    engine.session_manager.start.return_value = mock_session
    engine.session_manager.is_expired.return_value = False
    engine.session_manager.get.return_value = mock_session
    engine.question_bank.get.return_value = mock_question

    # Simulate answer() raising TimeoutError due to session expiration during answer
    engine.session_manager.answer.side_effect = TimeoutError("Assessment time has expired.")

    mock_result = MagicMock()
    mock_result.score = 0.5
    mock_result.passed = False
    mock_result.correct_answers = 1
    mock_result.total_questions = 2
    mock_result.topic_scores = []
    engine.evaluate_session.return_value = mock_result

    runner = TerminalOARunner(engine, duration_minutes=10)

    with patch("rich.prompt.Prompt.ask", side_effect=["", "a"]):
        with patch.object(runner, "_display_result") as mock_display:
            res = runner.run("session_123")
            assert res == mock_result
            mock_display.assert_called_once_with(mock_result)
            engine.evaluate_session.assert_called_once_with("session_123")

