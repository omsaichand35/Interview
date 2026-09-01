#!/usr/bin/env python3
"""
InterviewOS - Interactive Terminal Menu Launcher
"""
import os
import subprocess
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_screen()
        print("=" * 55)
        print("          ⚡ INTERVIEWOS RUNNER MENU ⚡")
        print("=" * 55)
        print(" 1.  Run Project Deep Dive Interview (GitHub)")
        print(" 2.  Run Technical Round Interview (PyTorch/ML)")
        print(" 3.  Run DSA Algorithmic Coding Round")
        print(" 4.  Run HR & Behavioral Interview")
        print(" 5.  Run Online Assessment (OA)")
        print(" 6.  Run AI Learning Mentor & Skill Tutor")
        print(" 7.  Run GitHub Repository Analyzer Agent")
        print(" 8.  Run Full Pytest Test Suite")
        print(" 0.  Exit")
        print("=" * 55)
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
        if choice == "0":
            print("\nExiting InterviewOS Launcher. Goodbye!\n")
            sys.exit(0)
            
        elif choice == "1":
            print("\nStarting Project Deep Dive Interview...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "project", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com", "--github", "https://github.com/omsaichand35/MCP"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")
            
        elif choice == "2":
            print("\nStarting Technical Round Interview...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "technical", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            print("\nStarting DSA Algorithmic Coding Round...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "dsa", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            print("\nStarting HR & Behavioral Interview...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "interview", "--type", "hr", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            print("\nStarting Online Assessment (OA)...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "oa", "--job", "data/input/job_descriptions/sample_jd.pdf", "--name", "Omsai Ramachandran", "--email", "omsai@example.com", "--questions", "5", "--duration", "20"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "6":
            print("\nStarting AI Learning Mentor...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "mentor", "--resume", "data/input/resumes/sample_resume.pdf", "--job", "data/input/job_descriptions/sample_jd.pdf"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "7":
            print("\nStarting GitHub Repository Analyzer Agent...\n")
            cmd = [sys.executable, "-m", "interviewos.cli", "project-analyze", "--github", "https://github.com/omsaichand35/MCP"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        elif choice == "8":
            print("\nRunning Test Suite (pytest)...\n")
            cmd = ["pytest", "tests/", "-v"]
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")

        else:
            print("\nInvalid choice. Please choose 0 to 8.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
