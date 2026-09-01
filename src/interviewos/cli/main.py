import argparse
import asyncio
from pathlib import Path

from .commands import InterviewOSApplication


def build_parser() -> argparse.ArgumentParser:
    """Create the InterviewOS CLI parser."""

    parser = argparse.ArgumentParser(
        prog="interviewos",
        description=(
            "InterviewOS AI interview preparation system."
        ),
    )

    parser.add_argument(
        "--resume",
        type=Path,
        required=False,
        help="Path to the candidate resume PDF.",
    )

    parser.add_argument(
        "--job",
        type=Path,
        required=False,
        help="Path to the job description PDF.",
    )

    parser.add_argument(
        "--knowledge",
        type=Path,
        default=None,
        help=(
            "Directory containing learning "
            "knowledge documents."
        ),
    )

    subparsers = parser.add_subparsers(dest="command")

# ---------------------------------------------------------
# OA
# ---------------------------------------------------------

    oa_parser = subparsers.add_parser(
        "oa",
        help="Create and run an objective assessment.",
    )

    oa_parser.add_argument(
        "--job",
        type=Path,
        required=True,
        help="Path to the job description.",
    )

    oa_parser.add_argument(
        "--name",
        required=True,
        help="Candidate name.",
    )

    oa_parser.add_argument(
        "--email",
        required=True,
        help="Candidate email.",
    )

    oa_parser.add_argument(
        "--questions",
        type=int,
        default=20,
        help="Number of questions.",
    )

    oa_parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Assessment duration in minutes.",
    )

    oa_parser.add_argument(
        "--threshold",
        type=float,
        default=0.60,
        help="Passing threshold between 0 and 1.",
    )

    oa_parser.add_argument(
        "--topics",
        type=str,
        default=None,
        help="Optional specific topics and weightages for the assessment (e.g. 'Python, SQL').",
    )

    project_parser = subparsers.add_parser(
        "project-analyze",
        help="Analyze a GitHub repository into a ProjectProfile.",
    )

    project_parser.add_argument(
        "--github",
        type=str,
        required=True,
        help="GitHub repository URL.",
    )

    interview_parser = subparsers.add_parser(
        "interview",
        help="Run an interactive interview.",
    )

    interview_parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=["dsa", "technical", "hr", "managerial", "project"],
        help="Type of interview to run.",
    )

    interview_parser.add_argument(
        "--job",
        type=Path,
        required=True,
        help="Path to the job description.",
    )

    interview_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Candidate name.",
    )

    interview_parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Candidate email.",
    )

    interview_parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Interview duration in minutes.",
    )

    interview_parser.add_argument(
        "--difficulty",
        type=str,
        default="medium",
        help="Interview difficulty.",
    )

    interview_parser.add_argument(
        "--github",
        type=str,
        required=False,
        help="GitHub repository URL for project interview.",
    )

    hiring_parser = subparsers.add_parser(
        "hiring",
        help="Run an orchestrated multi-round interview process.",
    )

    hiring_parser.add_argument(
        "--job",
        type=Path,
        required=True,
        help="Path to the job description.",
    )

    hiring_parser.add_argument(
        "--resume",
        type=Path,
        required=False,
        help="Path to the candidate resume.",
    )

    hiring_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Candidate name.",
    )

    hiring_parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Candidate email.",
    )

    hiring_parser.add_argument(
        "--plan",
        type=Path,
        required=False,
        help="Path to the interview plan JSON file.",
    )

    rank_parser = subparsers.add_parser(
        "rank",
        help="Rank candidates based on final evaluations.",
    )

    rank_parser.add_argument(
        "--job",
        type=Path,
        required=True,
        help="Path to the job description.",
    )

    rank_parser.add_argument(
        "--results",
        type=Path,
        required=True,
        help="Path to the directory containing candidate evaluation results.",
    )

    return parser


def main() -> None:
    """CLI entry point."""
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = build_parser()

    args = parser.parse_args()

    if args.command == "oa":

        application = InterviewOSApplication(
            resume_path=None,
            job_path=args.job,
        )

        asyncio.run(
            application.run_oa(
                candidate_name=args.name,
                candidate_email=args.email,
                total_questions=args.questions,
                duration_minutes=args.duration,
                threshold=args.threshold,
                topics=args.topics,
            )
        )

        return

    if args.command == "project-analyze":
        from interviewos.llm import create_llm_client
        from interviewos.interview.project import GitHubClient, ProjectAnalysisAgent
        from interviewos.config import get_settings
        
        settings = get_settings()
        
        llm = create_llm_client()
        github_client = GitHubClient(token=settings.github_token)
        agent = ProjectAnalysisAgent(llm, github_client)
        
        profile = asyncio.run(agent.analyze(args.github))
        
        print("\n======================================================================")
        print("PROJECT ANALYSIS COMPLETE")
        print("======================================================================")
        print(f"\nRepository: {profile.repository_name}")
        print(f"Summary: {profile.summary}")
        print(f"Languages: {', '.join(profile.languages)}")
        print(f"Technologies: {', '.join(profile.technologies)}")
        print(f"Architecture: {', '.join(profile.architecture)}")
        print(f"Important Files: {', '.join(profile.important_files)}")
        print(f"Interview Topics: {', '.join(profile.potential_interview_topics)}")
        print(f"Evidence Count: {len(profile.evidence)}")
        print(f"Status: {profile.analysis_completeness}")
        
        return

    if args.command == "interview":
        application = InterviewOSApplication(
            resume_path=None,
            job_path=args.job,
        )

        asyncio.run(
            application.run_interview(
                interview_type=args.type,
                candidate_name=args.name,
                candidate_email=args.email,
                duration_minutes=args.duration,
                difficulty=args.difficulty,
                github_url=getattr(args, "github", None),
            )
        )
        return

    if args.command == "hiring":

        application = InterviewOSApplication(
            resume_path=args.resume,
            job_path=args.job,
        )

        asyncio.run(
            application.run_hiring(
                candidate_name=args.name,
                candidate_email=args.email,
                plan_path=args.plan,
            )
        )
        return
        
    if args.command == "rank":
        
        application = InterviewOSApplication(
            resume_path=None,
            job_path=args.job,
        )
        
        application.run_ranking(results_dir=args.results)
        return

    # Fallback to mentor if command is "mentor" or not specified
    if not args.resume or not args.job:
        parser.error("The following arguments are required for mentor mode: --resume, --job")

    application = InterviewOSApplication(
        resume_path=args.resume,
        job_path=args.job,
    )

    application.run(
        knowledge_directory=args.knowledge
    )


if __name__ == "__main__":
    main()