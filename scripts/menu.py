#!/usr/bin/env python3
"""
InterviewOS - Interactive Rich Terminal UI Menu Launcher
Features dynamic profile setup, persistent context memory, and track dispatching.
"""
import os
import json
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.box import ROUNDED, HEAVY

console = Console()

PROFILE_FILE = Path("data/profile.json")

BANNER_ART = """[bold cyan]
  ___       _                           _               ___  ____  
 |_ _|_ __ | |_ ___ _ ____   ___      (_) _____      _/ _ \/ ___| 
  | || '_ \| __/ _ \ '__\ \ / / | ___ | |/ _ \ \ /\ / / | | \___ \ 
  | || | | | ||  __/ |   \ V /| |/ _ \| | (_) \ V  V /| |_| |___) |
 |___|_| |_|\__\___|_|    \_/ |_|\___//_|\___/ \_/\_/  \___/|____/ 
[/bold cyan]"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class UserProfile:
    def __init__(self):
        self.candidate_name = "Omsai Ramachandran"
        self.candidate_email = "omsai@example.com"
        self.job_path = "data/input/job_descriptions/sample_jd.pdf"
        self.resume_path = "data/input/resumes/sample_resume.pdf"
        self.last_github_url = "https://github.com/omsaichand35/MCP"

    @classmethod
    def load(cls) -> "UserProfile":
        profile = cls()
        if PROFILE_FILE.exists():
            try:
                data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
                profile.candidate_name = data.get("candidate_name", profile.candidate_name)
                profile.candidate_email = data.get("candidate_email", profile.candidate_email)
                profile.job_path = data.get("job_path", profile.job_path)
                profile.resume_path = data.get("resume_path", profile.resume_path)
                profile.last_github_url = data.get("last_github_url", profile.last_github_url)
                return profile
            except Exception:
                pass
        
        # First-time setup onboarding
        profile.onboarding()
        return profile

    def save(self):
        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "job_path": self.job_path,
            "resume_path": self.resume_path,
            "last_github_url": self.last_github_url,
        }
        PROFILE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def onboarding(self):
        clear_screen()
        console.print(BANNER_ART, justify="center")
        panel = Panel(
            "[bold white]Welcome to InterviewOS! Let's set up your candidate profile for this workspace.[/bold white]\n"
            "[dim]These settings will be remembered across sessions. You can edit them anytime.[/dim]",
            title="[bold green] Initial Profile Setup [/bold green]",
            border_style="green",
            box=ROUNDED
        )
        console.print(panel)
        console.print()

        self.candidate_name = Prompt.ask("[bold cyan]Enter Candidate Full Name[/bold cyan]", default=self.candidate_name).strip()
        self.candidate_email = Prompt.ask("[bold cyan]Enter Candidate Email[/bold cyan]", default=self.candidate_email).strip()
        self.job_path = Prompt.ask("[bold cyan]Enter Job Description PDF path[/bold cyan]", default=self.job_path).strip()
        self.resume_path = Prompt.ask("[bold cyan]Enter Resume PDF path[/bold cyan]", default=self.resume_path).strip()
        self.save()
        console.print("\n[bold green]✔ Profile initialized successfully![/bold green]\n")

    def edit_profile(self):
        clear_screen()
        console.print(BANNER_ART, justify="center")
        panel = Panel(
            "[bold white]Update your Candidate Profile, Job Description, or Resume PDF.[/bold white]",
            title="[bold cyan] Edit Profile & Target Files [/bold cyan]",
            border_style="cyan",
            box=ROUNDED
        )
        console.print(panel)
        console.print()

        self.candidate_name = Prompt.ask("[bold cyan]Candidate Full Name[/bold cyan]", default=self.candidate_name).strip()
        self.candidate_email = Prompt.ask("[bold cyan]Candidate Email[/bold cyan]", default=self.candidate_email).strip()
        self.job_path = Prompt.ask("[bold cyan]Job Description PDF path[/bold cyan]", default=self.job_path).strip()
        self.resume_path = Prompt.ask("[bold cyan]Resume PDF path[/bold cyan]", default=self.resume_path).strip()
        self.save()
        console.print("\n[bold green]✔ Profile & Context updated successfully![/bold green]")
        input("\nPress Enter to return to menu...")

def main():
    profile = UserProfile.load()

    while True:
        clear_screen()
        console.print(BANNER_ART, justify="center")
        console.print("[dim white]Autonomous Multi-Agent AI Interview & Mentoring Platform[/dim white]\n", justify="center")

        # Active Context Status Table
        ctx_table = Table(box=ROUNDED, border_style="dim cyan", show_header=True, header_style="bold cyan", expand=True)
        ctx_table.add_column("Current Profile & Target Context", style="bold white", width=30)
        ctx_table.add_column("Loaded Path / Setting", style="yellow")
        ctx_table.add_column("Status", style="bold green", justify="center", width=12)

        ctx_table.add_row("👤 Candidate", f"{profile.candidate_name} ({profile.candidate_email})", "[green]✔ Active[/green]")
        ctx_table.add_row("📄 Job Description", profile.job_path, "[green]✔ Loaded[/green]")
        ctx_table.add_row("📄 Candidate Resume", profile.resume_path, "[green]✔ Loaded[/green]")
        ctx_table.add_row("🧠 LLM Provider", "NVIDIA NIM / OpenAI", "[green]✔ Configured[/green]")

        console.print(ctx_table)
        console.print()

        # Tracks Menu Table
        menu_table = Table(box=ROUNDED, border_style="blue", show_header=True, header_style="bold magenta", expand=True)
        menu_table.add_column("#", style="bold cyan", justify="center", width=4)
        menu_table.add_column("Interview Track / Feature", style="bold white", width=34)
        menu_table.add_column("Description", style="dim white")

        menu_table.add_row("[bold cyan]1[/bold cyan]", "[bold white]Project Deep Dive Interview[/bold white]", "Autonomous GitHub AST repository analysis & architecture probing")
        menu_table.add_row("[bold cyan]2[/bold cyan]", "[bold white]Technical Architecture Round[/bold white]", "Deep dive into framework internals, PyTorch autograd & ML systems")
        menu_table.add_row("[bold cyan]3[/bold cyan]", "[bold white]DSA Algorithmic Coding Round[/bold white]", "Dynamic problem formulation, coding approach & complexity tradeoffs")
        menu_table.add_row("[bold cyan]4[/bold cyan]", "[bold white]HR & Behavioral Competency[/bold white]", "Situational questioning evaluated against role culture benchmarks")
        menu_table.add_row("[bold cyan]5[/bold cyan]", "[bold white]Online Assessment (OA)[/bold white]", "Timed 5-question test with automated rubric scoring")
        menu_table.add_row("[bold cyan]6[/bold cyan]", "[bold white]AI Learning Mentor & Tutor[/bold white]", "Skill gap roadmap, topic practice & adaptive learning agent")
        menu_table.add_row("[bold cyan]7[/bold cyan]", "[bold white]GitHub Repository Analyzer[/bold white]", "Standalone code hierarchy scanner, dependencies & AST agent")
        menu_table.add_row("[bold cyan]8[/bold cyan]", "[bold white]Run Full Pytest Test Suite[/bold white]", "Execute all 45 automated unit & integration test suites")
        menu_table.add_row("[bold yellow]C[/bold yellow]", "[bold yellow]Change Profile / JD / Resume[/bold yellow]", "Update your candidate name, email, target JD or resume")
        menu_table.add_row("[bold red]0[/bold red]", "[bold red]Exit Launcher[/bold red]", "Exit InterviewOS Terminal Environment")

        console.print(menu_table)
        console.print()

        choice = Prompt.ask("[bold green]Select Option (0-8 or C)[/bold green]", default="1").strip()
        
        if choice == "0":
            console.print("\n[bold cyan]Exiting InterviewOS Launcher. Good luck with your preparation![/bold cyan]\n")
            sys.exit(0)

        elif choice.upper() == "C":
            profile.edit_profile()

        elif choice == "1":
            console.print()
            github_url = Prompt.ask(
                "[bold cyan]Enter Candidate GitHub Repository URL[/bold cyan]",
                default=profile.last_github_url
            ).strip()
            profile.last_github_url = github_url
            profile.save()

            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "project",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email,
                "--github", github_url
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")
            
        elif choice == "2":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "technical",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "dsa",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "hr",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "oa",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email,
                "--questions", "5",
                "--duration", "20"
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "6":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "mentor",
                "--resume", profile.resume_path,
                "--job", profile.job_path
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "7":
            console.print()
            github_url = Prompt.ask(
                "[bold cyan]Enter Candidate GitHub Repository URL to Analyze[/bold cyan]",
                default=profile.last_github_url
            ).strip()
            profile.last_github_url = github_url
            profile.save()

            cmd = [
                sys.executable, "-m", "interviewos.cli", "project-analyze",
                "--github", github_url
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "8":
            cmd = ["pytest", "tests/", "-v"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        else:
            console.print("\n[red]Invalid choice. Please choose 0-8 or C.[/red]")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
