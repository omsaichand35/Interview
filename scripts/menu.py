#!/usr/bin/env python3
"""
InterviewOS - Interactive Rich Terminal UI Menu Launcher
Features dynamic profile setup, global difficulty, OA timer & question configuration, and track dispatching.
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
        self.candidate_name = "Omsaichand Boppudi"
        self.candidate_email = "omsaichandboppudi@gmail.com"
        self.job_path = "data/input/job_descriptions/sample_jd.pdf"
        self.resume_path = "data/input/resumes/sample_resume.pdf"
        self.last_github_url = "https://github.com/omsaichand35/MCP"
        self.voice_mode = True
        self.difficulty = "Medium"
        self.oa_questions = 5
        self.oa_duration = 20

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
                profile.voice_mode = data.get("voice_mode", profile.voice_mode)
                profile.difficulty = data.get("difficulty", profile.difficulty)
                profile.oa_questions = data.get("oa_questions", profile.oa_questions)
                profile.oa_duration = data.get("oa_duration", profile.oa_duration)
                return profile
            except Exception:
                pass
        
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
            "voice_mode": self.voice_mode,
            "difficulty": self.difficulty,
            "oa_questions": self.oa_questions,
            "oa_duration": self.oa_duration,
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
        self.job_path = Prompt.ask("[bold cyan]Enter Job Description PDF path[/bold cyan]", default=self.job_path).strip().strip('"\'')
        self.resume_path = Prompt.ask("[bold cyan]Enter Resume PDF path[/bold cyan]", default=self.resume_path).strip().strip('"\'')
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
        self.job_path = Prompt.ask("[bold cyan]Job Description PDF path[/bold cyan]", default=self.job_path).strip().strip('"\'')
        self.resume_path = Prompt.ask("[bold cyan]Resume PDF path[/bold cyan]", default=self.resume_path).strip().strip('"\'')
        self.save()
        console.print("\n[bold green]✔ Profile & Context updated successfully![/bold green]")
        input("\nPress Enter to return to menu...")

    def edit_settings(self):
        clear_screen()
        console.print(BANNER_ART, justify="center")
        panel = Panel(
            "[bold white]Configure Global Interview Difficulty and Online Assessment (OA) defaults.[/bold white]",
            title="[bold yellow] Global Difficulty & Assessment Settings [/bold yellow]",
            border_style="yellow",
            box=ROUNDED
        )
        console.print(panel)
        console.print()

        diff_choice = Prompt.ask(
            "[bold cyan]Select Global Interview Difficulty[/bold cyan]",
            choices=["Easy", "Medium", "Hard"],
            default=self.difficulty
        )
        self.difficulty = diff_choice

        try:
            q_count = Prompt.ask(
                "[bold cyan]Default Online Assessment (OA) Question Count[/bold cyan]",
                default=str(self.oa_questions)
            )
            self.oa_questions = max(1, int(q_count))
        except ValueError:
            pass

        try:
            dur = Prompt.ask(
                "[bold cyan]Default Online Assessment (OA) Duration (minutes)[/bold cyan]",
                default=str(self.oa_duration)
            )
            self.oa_duration = max(5, int(dur))
        except ValueError:
            pass

        self.save()
        console.print(f"\n[bold green]✔ Settings saved: Difficulty={self.difficulty}, OA={self.oa_questions} questions in {self.oa_duration}m[/bold green]")
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
        ctx_table.add_column("Status", style="bold green", justify="center", width=14)

        voice_status = "[bold green]✔ Enabled (Live Rounds)[/bold green]" if profile.voice_mode else "[dim]Disabled (Text-only)[/dim]"
        diff_color = "green" if profile.difficulty == "Easy" else "yellow" if profile.difficulty == "Medium" else "red"

        ctx_table.add_row("👤 Candidate", f"{profile.candidate_name} ({profile.candidate_email})", "[green]✔ Active[/green]")
        ctx_table.add_row("📄 Job Description", profile.job_path, "[green]✔ Loaded[/green]")
        ctx_table.add_row("📄 Candidate Resume", profile.resume_path, "[green]✔ Loaded[/green]")
        ctx_table.add_row("🎯 Global Difficulty", f"[{diff_color}]{profile.difficulty}[/{diff_color}]", "[green]✔ Set[/green]")
        ctx_table.add_row("⏱ OA Configuration", f"{profile.oa_questions} Questions • {profile.oa_duration} Minutes", "[green]✔ Set[/green]")
        ctx_table.add_row("🎙 Voice Mode (TTS & STT)", "Spoken AI audio + Mic in interviews", voice_status)

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
        menu_table.add_row("[bold cyan]5[/bold cyan]", "[bold white]Online Assessment (OA)[/bold white]", f"Timed test with automated scoring ({profile.oa_questions} Qs, {profile.oa_duration} mins)")
        menu_table.add_row("[bold cyan]6[/bold cyan]", "[bold white]AI Learning Mentor & Tutor[/bold white]", "Skill gap roadmap, topic practice & adaptive learning agent")
        menu_table.add_row("[bold cyan]7[/bold cyan]", "[bold white]GitHub Repository Analyzer[/bold white]", "Standalone code hierarchy scanner, dependencies & AST agent")
        menu_table.add_row("[bold cyan]8[/bold cyan]", "[bold white]Full Hiring Pipeline (End-to-End)[/bold white]", "Autonomous multi-round evaluation across OA, Tech, Project & HR")
        menu_table.add_row("[bold yellow]D[/bold yellow]", "[bold yellow]Change Difficulty & OA Settings[/bold yellow]", f"Difficulty: {profile.difficulty} • OA: {profile.oa_questions} Qs / {profile.oa_duration}m")
        menu_table.add_row("[bold magenta]V[/bold magenta]", "[bold magenta]Toggle Voice Mode (TTS/STT)[/bold magenta]", f"Currently: {'[green]ON (Live Interviews)[/green]' if profile.voice_mode else '[red]OFF (Text-only)[/red]'}")
        menu_table.add_row("[bold yellow]C[/bold yellow]", "[bold yellow]Change Profile / JD / Resume[/bold yellow]", "Update your candidate name, email, target JD or resume")
        menu_table.add_row("[bold red]0[/bold red]", "[bold red]Exit Launcher[/bold red]", "Exit InterviewOS Terminal Environment")

        console.print(menu_table)
        console.print()

        choice = Prompt.ask("[bold green]Select Option (0-8, D, V, or C)[/bold green]", default="1").strip()
        
        if choice == "0":
            console.print("\n[bold cyan]Exiting InterviewOS Launcher. Good luck with your preparation![/bold cyan]\n")
            sys.exit(0)

        elif choice.upper() == "D":
            profile.edit_settings()

        elif choice.upper() == "V":
            profile.voice_mode = not profile.voice_mode
            profile.save()
            console.print(f"\n[bold green]✔ Voice Mode {'Enabled (TTS + STT Active in Interviews)' if profile.voice_mode else 'Disabled (Text-only)'}![/bold green]")
            import time
            time.sleep(1.0)

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
                "--difficulty", profile.difficulty,
                "--github", github_url
            ]
            if profile.voice_mode:
                cmd.append("--voice")
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")
            
        elif choice == "2":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "technical",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email,
                "--difficulty", profile.difficulty,
            ]
            if profile.voice_mode:
                cmd.append("--voice")
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "dsa",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email,
                "--difficulty", profile.difficulty,
            ]
            if profile.voice_mode:
                cmd.append("--voice")
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            cmd = [
                sys.executable, "-m", "interviewos.cli", "interview",
                "--type", "hr",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email,
                "--difficulty", profile.difficulty,
            ]
            if profile.voice_mode:
                cmd.append("--voice")
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            console.print()
            try:
                q_count = Prompt.ask(
                    "[bold cyan]Enter Number of OA Questions[/bold cyan]",
                    default=str(profile.oa_questions)
                ).strip()
                oa_q = max(1, int(q_count))
            except ValueError:
                oa_q = profile.oa_questions

            try:
                dur_str = Prompt.ask(
                    "[bold cyan]Enter OA Duration (minutes)[/bold cyan]",
                    default=str(profile.oa_duration)
                ).strip()
                oa_d = max(5, int(dur_str))
            except ValueError:
                oa_d = profile.oa_duration

            profile.oa_questions = oa_q
            profile.oa_duration = oa_d
            profile.save()

            cmd = [
                sys.executable, "-m", "interviewos.cli", "oa",
                "--job", profile.job_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email,
                "--questions", str(oa_q),
                "--duration", str(oa_d)
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
            console.print()
            github_url = Prompt.ask(
                "[bold cyan]Enter Candidate GitHub Repository URL for Pipeline[/bold cyan]",
                default=profile.last_github_url
            ).strip()
            profile.last_github_url = github_url
            profile.save()

            cmd = [
                sys.executable, "-m", "interviewos.cli", "hiring",
                "--job", profile.job_path,
                "--resume", profile.resume_path,
                "--name", profile.candidate_name,
                "--email", profile.candidate_email
            ]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()
