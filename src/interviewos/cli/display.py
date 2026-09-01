"""
InterviewOS Rich Display Formatter for Mentor, Analysis, and Plans
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.box import ROUNDED, SIMPLE, DOUBLE_EDGE

from interviewos.models import (
    JobProfile,
    ResumeProfile,
    SkillGapReport,
)
from interviewos.models.plan import PreparationPlan, TopicNode

console = Console()


def print_header(title: str) -> None:
    """Print a styled section banner."""
    console.print(f"\n[bold cyan]─── {title} ──────────────────────────────────────[/bold cyan]\n")


def print_resume(profile: ResumeProfile) -> None:
    """Display analyzed resume with Rich Panel and Table."""
    table = Table(box=ROUNDED, border_style="green", show_header=True, header_style="bold green")
    table.add_column("Skill Name", style="white")
    table.add_column("Proficiency", justify="center", style="bold cyan")

    for skill in profile.skills:
        table.add_row(skill.name, skill.level.value.capitalize())

    content = f"[bold white]Candidate:[/bold white] [bold green]{profile.candidate_name or 'N/A'}[/bold green]\n"
    if profile.summary:
        content += f"\n[dim italic]{profile.summary}[/dim italic]\n"

    panel = Panel(
        table,
        title="[bold green]📄 RESUME ANALYSIS[/bold green]",
        subtitle=f"Candidate: [bold]{profile.candidate_name or 'N/A'}[/bold] • {len(profile.skills)} skills extracted",
        border_style="green",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)


def print_job(profile: JobProfile) -> None:
    """Display analyzed job description with Rich Panel and Table."""
    table = Table(box=ROUNDED, border_style="cyan", show_header=True, header_style="bold cyan")
    table.add_column("Skill / Requirement", style="white")
    table.add_column("Expected Depth", justify="center", style="bold yellow")
    table.add_column("Requirement Type", justify="center", style="dim")

    for skill in profile.required_skills:
        table.add_row(skill.name, skill.expected_level.value.capitalize(), "[bold red]Required[/bold red]")

    if profile.preferred_skills:
        for skill in profile.preferred_skills:
            table.add_row(skill.name, skill.expected_level.value.capitalize(), "[dim cyan]Preferred[/dim cyan]")

    panel = Panel(
        table,
        title="[bold cyan]💼 JOB DESCRIPTION ANALYSIS[/bold cyan]",
        subtitle=f"Target Role: [bold yellow]{profile.title}[/bold yellow]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)


def print_skill_gaps(report: SkillGapReport) -> None:
    """Display candidate skill gaps & strengths."""
    table = Table(box=ROUNDED, border_style="yellow", show_header=True, header_style="bold yellow")
    table.add_column("Competency / Skill Area", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Priority", justify="center", style="bold")

    if report.strengths:
        for skill in report.strengths:
            table.add_row(skill.name, "[bold green]✔ Strength[/bold green]", "[dim]Low[/dim]")

    if report.missing_skills:
        for skill in report.missing_skills:
            table.add_row(skill.name, "[bold red]✖ Missing[/bold red]", "[bold red]High[/bold red]")

    if report.gaps:
        for gap in report.gaps:
            table.add_row(gap.skill, f"[yellow]▲ Gap ({gap.gap_score:.1f})[/yellow]", f"[bold yellow]{gap.priority}[/bold yellow]")

    panel = Panel(
        table,
        title="[bold yellow]🎯 TARGET SKILL GAP ANALYSIS[/bold yellow]",
        border_style="yellow",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)


def print_learning_plan(plan: PreparationPlan) -> None:
    """Display personalized preparation roadmap as a tree."""
    tree = Tree(f"[bold cyan]🎯 Goal: {plan.goal}[/bold cyan] [bold green]({plan.overall_mastery}% Mastery)[/bold green]")

    def add_nodes(parent_tree: Tree, node: TopicNode):
        score_color = "green" if node.mastery_score >= 70 else "yellow" if node.mastery_score >= 40 else "red"
        node_branch = parent_tree.add(
            f"[bold white]{node.title}[/bold white] "
            f"[{score_color}]({node.mastery_score}% mastery)[/{score_color}] "
            f"[dim]• Priority: {node.priority.value}[/dim]"
        )
        for child in node.subtopics:
            add_nodes(node_branch, child)

    for topic in plan.topics:
        add_nodes(tree, topic)

    panel = Panel(
        tree,
        title="[bold magenta]📚 ADAPTIVE LEARNING ROADMAP[/bold magenta]",
        border_style="magenta",
        box=ROUNDED,
        padding=(1, 2)
    )
    console.print()
    console.print(panel)


def print_help() -> None:
    """Display interactive mentor commands."""
    table = Table(box=SIMPLE, show_header=True, header_style="bold cyan")
    table.add_column("Command", style="bold yellow")
    table.add_column("Description", style="white")

    table.add_row("/help", "Show available mentor commands")
    table.add_row("/state", "Show your current learning & mastery state")
    table.add_row("/practice <topic>", "Generate a tailored interactive practice question")
    table.add_row("/review", "Targeted review on your weakest topic")
    table.add_row("/quit", "Conclude mentorship session and save progress")

    panel = Panel(
        table,
        title="[bold cyan]💡 Mentor Interactive Commands[/bold cyan]",
        subtitle="[dim]You can also type any question naturally to discuss with the AI Mentor.[/dim]",
        border_style="cyan",
        box=ROUNDED
    )
    console.print()
    console.print(panel)