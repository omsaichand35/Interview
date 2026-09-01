"""
InterviewOS Terminal Online Assessment (OA) Runner with Real-Time Timer & Rich TUI
"""
import string
import time
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.box import ROUNDED, HEAVY, SIMPLE

from interviewos.models import (
    AssessmentQuestion,
    CandidateAnswer,
)
from .oa import OAEngine

console = Console()


class TerminalOARunner:
    """Run an objective assessment in the terminal with timer and Rich styling."""

    def __init__(
        self,
        engine: OAEngine,
        duration_minutes: int = 20,
    ) -> None:
        self.engine = engine
        self.duration_minutes = duration_minutes

    def run(
        self,
        session_id: str,
    ):
        """Run an existing assessment session with real-time countdown tracking."""

        session = self.engine.session_manager.start(session_id)
        start_time = datetime.now()
        total_seconds = self.duration_minutes * 60

        # Start Header Panel
        table = Table(box=SIMPLE, show_header=False)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("🎯 Assessment Role", f"[bold yellow]{session.role}[/bold yellow]")
        table.add_row("📝 Question Count", f"{len(session.question_ids)} questions")
        table.add_row("⏱ Time Limit", f"{self.duration_minutes} minutes")

        panel = Panel(
            table,
            title="[bold cyan]⚡ ONLINE ASSESSMENT (OA)[/bold cyan]",
            subtitle="[dim]Timer will begin once you start • Answer each question by typing option letter (e.g. A)[/dim]",
            border_style="cyan",
            box=ROUNDED,
            padding=(1, 2)
        )
        console.print()
        console.print(panel)
        console.print()

        Prompt.ask("[bold green]Press Enter to begin the assessment[/bold green]")
        start_time = datetime.now()

        for index, question_id in enumerate(session.question_ids, start=1):
            # Calculate real-time timer
            elapsed = int((datetime.now() - start_time).total_seconds())
            remaining = max(0, total_seconds - elapsed)
            elapsed_m, elapsed_s = divmod(elapsed, 60)
            rem_m, rem_s = divmod(remaining, 60)

            timer_display = f"⏱ {rem_m:02d}:{rem_s:02d} left ({elapsed_m:02d}:{elapsed_s:02d} / {self.duration_minutes:02d}:00)"

            if remaining <= 0:
                console.print("\n[bold red]⏱ TIME UP! Automatically submitting assessment...[/bold red]\n")
                break

            question = self.engine.question_bank.get(question_id)
            if question is None:
                continue

            mapping = self._display_question(
                question,
                index,
                len(session.question_ids),
                timer_display
            )

            answer = self._collect_answer(
                question,
                mapping
            )

            if answer is None: # Conclude early
                console.print("\n[dim]Candidate concluded assessment early.[/dim]")
                break

            self.engine.session_manager.answer(
                session_id,
                answer,
            )

        with console.status("[bold cyan]📊 Scoring assessment against benchmark...[/bold cyan]", spinner="dots"):
            self.engine.session_manager.submit(session_id)
            result = self.engine.evaluate_session(session_id)

        self._display_result(result)
        return result

    def _display_question(
        self,
        question: AssessmentQuestion,
        number: int,
        total: int,
        timer_display: str,
    ) -> dict[str, str]:
        """Display one question with options inside a styled Rich panel."""
        letters = string.ascii_lowercase

        options_text = []
        mapping = {}
        for i, option in enumerate(question.options):
            letter = letters[i].upper()
            mapping[letter] = option.id
            options_text.append(f"  [bold cyan]({letter})[/bold cyan] {option.text}")

        options_block = "\n".join(options_text)
        content = f"{question.question}\n\n{options_block}"

        panel = Panel(
            content,
            title=f"[bold green] Question {number} of {total} [/bold green]  [bold yellow]• {timer_display}[/bold yellow]",
            subtitle="[dim]Type the option letter (e.g., A, B) and press Enter • Type 'done' to submit[/dim]",
            border_style="blue",
            box=ROUNDED,
            padding=(1, 2)
        )
        console.print()
        console.print(panel)
        return mapping

    def _collect_answer(
        self,
        question: AssessmentQuestion,
        mapping: dict[str, str],
    ) -> CandidateAnswer | None:
        """Collect an answer from the candidate."""

        while True:
            console.print()
            try:
                raw = Prompt.ask("[bold green]Your Choice ❯[/bold green]").strip()
            except (KeyboardInterrupt, EOFError):
                return None

            if not raw:
                console.print("[dim yellow]Please enter an option letter.[/dim yellow]")
                continue

            if raw.lower() in ('done', 'exit', 'quit', 'finish', 'submit'):
                return None

            if len(selected) != 1:
                console.print("[dim yellow]Please choose exactly one option (e.g. A).[/dim yellow]")
                continue

            chosen_letter = selected[0]
            if chosen_letter not in mapping:
                console.print(f"[red]Invalid option. Choose from: {', '.join(sorted(mapping.keys()))}[/red]")
                continue

            return CandidateAnswer(
                question_id=question.id,
                selected_options=[mapping[chosen_letter]],
            )

    def _display_result(
        self,
        result,
    ) -> None:
        """Display the final assessment scorecard result."""
        score_pct = int(result.score * 100)
        status_tag = "[bold white on green]  PASSED (RECOMMEND ADVANCE)  [/bold white on green]" if result.passed else "[bold white on red]  NOT PASSED (BELOW BAR)  [/bold white on red]"
        border_style = "green" if result.passed else "red"

        table = Table(box=ROUNDED, border_style="dim white", show_header=True, header_style="bold cyan")
        table.add_column("Topic / Domain Area", style="white")
        table.add_column("Correct / Total", justify="center", style="bold")
        table.add_column("Accuracy", justify="right", style="bold yellow")

        if result.topic_scores:
            for ts in result.topic_scores:
                table.add_row(
                    ts.topic,
                    f"{ts.correct_answers} / {ts.total_questions}",
                    f"{ts.score * 100:.1f}%"
                )
        else:
            table.add_row("General Technical Assessment", f"{result.correct_answers} / {result.total_questions}", f"{score_pct}%")

        scorecard = Panel(
            table,
            title="[bold cyan]🏆 ONLINE ASSESSMENT SCORECARD[/bold cyan]",
            subtitle=f"Overall Score: [bold]{score_pct}%[/bold] ({result.correct_answers}/{result.total_questions} correct) • {status_tag}",
            border_style=border_style,
            box=HEAVY,
            padding=(1, 2)
        )
        console.print()
        console.print(scorecard)
        console.print()