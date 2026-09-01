from interviewos.models import (
    JobProfile,
    ResumeProfile,
    SkillGapReport,
)
from interviewos.models.plan import PreparationPlan, TopicNode


def print_header(title: str) -> None:
    """Print a CLI section header."""

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def print_resume(profile: ResumeProfile) -> None:
    """Display the analyzed resume."""

    print_header("RESUME ANALYSIS")

    print(f"Candidate: {profile.candidate_name}")

    if profile.summary:
        print(f"\nSummary:\n{profile.summary}")

    print("\nSkills:")

    for skill in profile.skills:
        print(
            f"  • {skill.name} "
            f"[{skill.level.value}]"
        )


def print_job(profile: JobProfile) -> None:
    """Display the analyzed job description."""

    print_header("JOB ANALYSIS")

    print(f"Role: {profile.title}")

    print("\nRequired skills:")

    for skill in profile.required_skills:
        print(
            f"  • {skill.name} "
            f"[{skill.expected_level.value}]"
        )

    if profile.preferred_skills:
        print("\nPreferred skills:")

        for skill in profile.preferred_skills:
            print(
                f"  • {skill.name} "
                f"[{skill.expected_level.value}]"
            )


def print_skill_gaps(
    report: SkillGapReport,
) -> None:
    """Display candidate skill gaps."""

    print_header("SKILL GAP ANALYSIS")

    if report.strengths:
        print("Strengths:")

        for skill in report.strengths:
            print(
                f"  + {skill.name}"
            )

    if report.missing_skills:
        print("\nMissing skills:")

        for skill in report.missing_skills:
            print(
                f"  - {skill.name}"
            )

    if report.gaps:
        print("\nGaps:")

        for gap in report.gaps:
            print(
                f"  • {gap.skill}"
                f" | gap={gap.gap_score:.2f}"
                f" | priority={gap.priority}"
            )


def print_learning_plan(
    plan: PreparationPlan,
) -> None:
    """Display the generated preparation plan."""

    print_header("PREPARATION PLAN")

    print(f"Goal: {plan.goal}")
    print(f"Overall Mastery: {plan.overall_mastery}%")

    print("\nTopics:")

    def print_node(node: TopicNode, indent: int = 0) -> None:
        prefix = "  " * indent
        connector = "|--" if indent > 0 else ""
        print(f"{prefix}{connector} {node.title} [{node.mastery_score}%] (Priority: {node.priority.value}, State: {node.state.value})")
        for child in node.subtopics:
            print_node(child, indent + 1)

    for topic in plan.topics:
        print_node(topic)


def print_help() -> None:
    """Display mentor commands."""

    print(
        """
Mentor commands:

  /help
      Show this help.

  /state
      Show your current learning state.

  /practice <topic>
      Generate a practice question.

  /review
      Review a weak topic.

  /quit
      Exit the mentor.

Anything else is treated as a normal mentor message.
"""
    )