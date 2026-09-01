#!/usr/bin/env python3
"""
InterviewOS - Interactive Rich Terminal UI Menu Launcher
"""
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.box import ROUNDED, HEAVY, DOUBLE_EDGE

console = Console()

BANNER_ART = """[bold cyan]
  ___       _                           _               ___  ____  
 |_ _|_ __ | |_ ___ _ ____   ___      (_) _____      _/ _ \/ ___| 
  | || '_ \| __/ _ \ '__\ \ / / | ___ | |/ _ \ \ /\ / / | | \___ \ 
  | || | | | ||  __/ |   \ V /| |/ _ \| | (_) \ V  V /| |_| |___) |
 |___|_| |_|\__\___|_|    \_/ |_|\___//_|\___/ \_/\_/  \___/|____/ 
[/bold cyan]"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        console.print(BANNER_ART, justify="center")
        console.print("[dim white]Autonomous Multi-Agent AI Interview & Mentoring Platform[/dim white]\n", justify="center")

        # Status Table / Context
        ctx_table = Table(box=ROUNDED, border_style="dim cyan", show_header=True, header_style="bold cyan", expand=True)
        ctx_table.add_column("Key Config", style="bold white", width=22)
        ctx_table.add_column("Active Setting / Resource", style="yellow")
        ctx_table.add_column("Status", style="bold green", justify="center", width=12)

        ctx_table.add_row("🎯 Candidate Name", "Omsai Ramachandran (omsai@example.com)", "[green]✔ Loaded[/green]")
        ctx_table.add_row("📄 Job Description", "data/input/job_descriptions/sample_jd.pdf", "[green]✔ Loaded[/green]")
        ctx_table.add_row("👤 Candidate Resume", "data/input/resumes/sample_resume.pdf", "[green]✔ Loaded[/green]")
        ctx_table.add_row("🔗 Target GitHub Repo", "https://github.com/omsaichand35/MCP", "[green]✔ Connected[/green]")
        ctx_table.add_row("🧠 LLM Provider", "NVIDIA NIM (nemotron-3-super-120b)", "[green]✔ Online[/green]")

        console.print(ctx_table)
        console.print()

        # Tracks Menu Table
        menu_table = Table(box=ROUNDED, border_style="blue", show_header=True, header_style="bold magenta", expand=True)
        menu_table.add_column("#", style="bold cyan", justify="center", width=4)
        menu_table.add_column("Interview Track / Tool", style="bold white", width=34)
        menu_table.add_column("Description & Evaluation Mechanics", style="dim white")

        menu_table.add_row("[bold cyan]1[/bold cyan]", "[bold white]Project Deep Dive (GitHub)[/bold white]", "Autonomous AST analysis of candidate repository with design probing")
        menu_table.add_row("[bold cyan]2[/bold cyan]", "[bold white]Technical Architecture Round[/bold white]", "Deep dive into framework internals, PyTorch autograd & distributed ML")
        menu_table.add_row("[bold cyan]3[/bold cyan]", "[bold white]DSA Algorithmic Coding Round[/bold white]", "Dynamic problem formulation, complexity tradeoffs & solution analysis")
        menu_table.add_row("[bold cyan]4[/bold cyan]", "[bold white]HR & Behavioral Competency[/bold white]", "Situational questioning evaluated against role culture benchmarks")
        menu_table.add_row("[bold cyan]5[/bold cyan]", "[bold white]Online Assessment (OA)[/bold white]", "Timed 5-question multiple-choice/coding test with automated grading")
        menu_table.add_row("[bold cyan]6[/bold cyan]", "[bold white]AI Learning Mentor & Tutor[/bold white]", "Skill gap analysis, mastery tracking & interactive practice sessions")
        menu_table.add_row("[bold cyan]7[/bold cyan]", "[bold white]GitHub Repository Analyzer[/bold white]", "Standalone code hierarchy scanner, dependencies & AST agent")
        menu_table.add_row("[bold cyan]8[/bold cyan]", "[bold white]Run Full Pytest Test Suite[/bold white]", "Execute all 45 automated unit & integration test suites")
        menu_table.add_row("[bold red]0[/bold red]", "[bold red]Exit Launcher[/bold red]", "Exit InterviewOS Terminal Environment")

        console.print(menu_table)
        console.print()

        choice = Prompt.ask("[bold green]Select Option (0-8)[/bold green]", default="1").strip()
        
        if choice == "0":
            console.print("\n[bold cyan]Exiting InterviewOS Launcher. Good luck with your interviews![/bold cyan]\n")
            sys.exit(0)
            
        elif choice == "1":
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "project", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com", "--github", "https://github.com/omsaichand35/MCP"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")
            
        elif choice == "2":
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "technical", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "dsa", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "hr", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            cmd = [sys.executable, "-m", "interviewos.cli", "oa", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com", "--questions", "5", "--duration", "20"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "6":
            cmd = [sys.executable, "-m", "interviewos.cli", "mentor", "--resume", "data/input/resumes/sample_resume.pdf", "--job", "data/input/job_descriptions/sample_jd.pdf"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "7":
            cmd = [sys.executable, "-m", "interviewos.cli", "project-analyze", "--github", "https://github.com/omsaichand35/MCP"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "8":
            cmd = ["pytest", "tests/", "-v"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        else:
            console.print("\n[red]Invalid choice. Please choose 0 to 8.[/red]")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
