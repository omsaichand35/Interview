"""
InterviewOS Terminal UI (TUI) Engine
Provides modern, rich terminal styling, spinners, cards, and interactive layouts.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.box import ROUNDED, DOUBLE_EDGE, HEAVY, SIMPLE

# Initialize Rich Console
console = Console()

BANNER_ART = """[bold cyan]
  ___       _                           _               ___  ____  
 |_ _|_ __ | |_ ___ _ ____   ___      (_) _____      _/ _ \/ ___| 
  | || '_ \| __/ _ \ '__\ \ / / | ___ | |/ _ \ \ /\ / / | | \___ \ 
  | || | | | ||  __/ |   \ V /| |/ _ \| | (_) \ V  V /| |_| |___) |
 |___|_| |_|\__\___|_|    \_/ |_|\___//_|\___/ \_/\_/  \___/|____/ 
[/bold cyan]"""

def print_banner(subtitle: str = "Autonomous Multi-Agent Interview & Mentoring Engine") -> None:
    """Print the InterviewOS header banner."""
    console.print(BANNER_ART, justify="center")
    console.print(f"[dim white]{subtitle}[/dim white]\n", justify="center")

def print_round_header(
    round_name: str,
    role: str,
    candidate_name: str,
    duration_minutes: int,
    extra_info: Optional[Dict[str, str]] = None
) -> None:
    """Display round introduction panel."""
    table = Table(box=SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("🎯 Interview Track", f"[bold yellow]{round_name.upper()}[/bold yellow]")
    table.add_row("💼 Target Role", f"[bold white]{role}[/bold white]")
    table.add_row("👤 Candidate", f"[bold green]{candidate_name}[/bold green]")
    table.add_row("⏱ Duration", f"{duration_minutes} minutes")

    if extra_info:
        for k, v in extra_info.items():
            table.add_row(k, v)

    instructions = Text("\n💡 Note: Type 'done' or 'exit' at any prompt to conclude and view your scorecard.", style="dim italic")
    
    panel = Panel(
        table,
        title=f"[bold cyan]⚡ {round_name.upper()} ROUND[/bold cyan]",
        subtitle=instructions,
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)
    console.print()

def print_question_card(
    question_idx: int,
    total_questions: int,
    question_text: str,
    prompt_id: Optional[str] = None,
    competency: Optional[str] = None,
    topic: Optional[str] = None,
    timer_str: Optional[str] = None,
    voice_mode: bool = False
) -> None:
    """Render an interviewer question inside a styled panel."""
    header_parts = []
    if competency:
        header_parts.append(f"[bold magenta]• {competency}[/bold magenta]")
    if timer_str:
        header_parts.append(f"[bold yellow]• {timer_str}[/bold yellow]")
    if prompt_id:
        header_parts.append(f"[dim cyan]({prompt_id})[/dim cyan]")

    header = " ".join(header_parts) if header_parts else ""
    
    panel = Panel(
        f"{question_text}",
        title=f"[bold green] Question {question_idx} of {total_questions} [/bold green] {header}",
        subtitle=f"[dim]Type answer below and press Enter • Type 'done' to finish early[/dim]",
        border_style="blue",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)

    # Voice TTS Output only when explicitly in voice mode (interviews)
    if voice_mode:
        try:
            from interviewos.voice import get_voice_engine
            get_voice_engine().speak(question_text)
        except Exception:
            pass

def prompt_candidate_answer(voice_mode: bool = False) -> str:
    """Prompt the candidate for input with optional Speech-to-Text (STT) mic listening."""
    console.print()
    if voice_mode:
        try:
            from interviewos.voice import get_voice_engine
            spoken = get_voice_engine().listen(timeout=8, phrase_time_limit=45)
            if spoken:
                console.print(f"[bold green]Candidate [Spoken Voice] ❯ [/bold green][white]{spoken}[/white]")
                confirm = Prompt.ask("[dim]Press Enter to submit spoken answer, or type to override[/dim]", default=spoken)
                return confirm.strip()
        except Exception:
            pass

    try:
        ans = Prompt.ask("[bold green]Candidate [You] ❯[/bold green]")
        return ans.strip()
    except (KeyboardInterrupt, EOFError):
        return "exit"

@contextmanager
def show_thinking_spinner(message: str = "🤖 AI Interviewer is evaluating response..."):
    """Animated thinking spinner context manager."""
    with console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots"):
        yield

def print_evaluation_card(
    score: float,
    strengths: Optional[List[str]] = None,
    weaknesses: Optional[List[str]] = None,
    feedback: Optional[str] = None,
    follow_up_hint: Optional[str] = None
) -> None:
    """Render real-time AI answer assessment feedback."""
    score_pct = int(score * 100) if score <= 1.0 else int(score)
    
    if score_pct >= 80:
        score_badge = f"[bold black on green] SCORE: {score_pct}% (STRONG HIRE) [/bold black on green]"
        border_color = "green"
    elif score_pct >= 65:
        score_badge = f"[bold black on yellow] SCORE: {score_pct}% (MEETS BAR) [/bold black on yellow]"
        border_color = "yellow"
    else:
        score_badge = f"[bold white on red] SCORE: {score_pct}% (NEEDS IMPROVEMENT) [/bold white on red]"
        border_color = "red"

    rows = []
    if feedback:
        rows.append(f"[bold white]{feedback}[/bold white]\n")

    if strengths:
        rows.append("[bold green]✔ Observed Strengths:[/bold green]")
        for s in strengths:
            rows.append(f"  [dim green]•[/dim green] [green]{s}[/green]")
        rows.append("")

    if weaknesses:
        rows.append("[bold yellow]▲ Areas to Expand / Probe:[/bold yellow]")
        for w in weaknesses:
            rows.append(f"  [dim yellow]•[/dim yellow] [yellow]{w}[/yellow]")
        rows.append("")

    if follow_up_hint:
        rows.append(f"[dim cyan]ℹ Next Question Angle: {follow_up_hint}[/dim cyan]")

    body_text = "\n".join(rows).strip()

    panel = Panel(
        body_text if body_text else "[dim]Answer evaluated successfully.[/dim]",
        title=f"[bold]📊 AI Answer Evaluation[/bold]  {score_badge}",
        border_style=border_color,
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)

def print_final_scorecard(
    round_name: str,
    candidate_name: str,
    overall_score: float,
    assessments: Optional[List[Any]] = None
) -> None:
    """Display final interview scorecard summary table."""
    score_pct = int(overall_score * 100) if overall_score <= 1.0 else int(overall_score)
    
    if score_pct >= 80:
        decision_badge = "[bold white on green]  RECOMMEND TO ADVANCE (STRONG HIRE)  [/bold white on green]"
        border_style = "green"
    elif score_pct >= 65:
        decision_badge = "[bold black on yellow]  LEAN ADVANCE (MEETS BAR)  [/bold black on yellow]"
        border_style = "yellow"
    else:
        decision_badge = "[bold white on red]  REJECT / RETEST (BELOW BENCHMARK)  [/bold white on red]"
        border_style = "red"

    table = Table(box=ROUNDED, border_style="dim white", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Evaluation Parameter / Competency", style="white")
    table.add_column("Score", justify="right", style="bold")
    table.add_column("Assessment Status", style="italic")

    if assessments:
        for idx, item in enumerate(assessments, 1):
            sc = getattr(item, "score", 0.8)
            sc_pct = int(sc * 100) if sc <= 1.0 else int(sc)
            st = getattr(item, "feedback", "Evaluated against benchmark")
            tag = "[green]Pass[/green]" if sc_pct >= 65 else "[red]Review[/red]"
            table.add_row(str(idx), getattr(item, "competency", f"Question {idx}"), f"{sc_pct}%", tag)
    else:
        table.add_row("1", "Technical & Conceptual Depth", f"{score_pct}%", "[green]Pass[/green]")
        table.add_row("2", "Problem Formulation & Correctness", f"{score_pct}%", "[green]Pass[/green]")
        table.add_row("3", "Communication & Tradeoffs", f"{score_pct}%", "[green]Pass[/green]")

    scorecard_panel = Panel(
        table,
        title=f"[bold cyan]🏆 {round_name.upper()} FINAL SCORECARD[/bold cyan]",
        subtitle=f"Candidate: [bold]{candidate_name}[/bold] • Final Grade: [bold]{score_pct}%[/bold] • {decision_badge}",
        border_style=border_style,
        box=HEAVY,
        padding=(1, 2)
    )
    console.print()
    console.print(scorecard_panel)
    console.print()
