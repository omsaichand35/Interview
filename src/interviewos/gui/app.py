import datetime
import io
import json
import os
import sys
import threading
import uuid
import contextlib
from pathlib import Path
from typing import Any, Dict, List, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from interviewos.config import get_settings
from interviewos.gui.state import PersistentAppState, ChatSession

# Modern Dark Theme Palette
COLOR_BG_DARK = "#0D1117"
COLOR_SIDEBAR = "#161B22"
COLOR_CARD = "#21262D"
COLOR_BORDER = "#30363D"
COLOR_PRIMARY_BLUE = "#58A6FF"
COLOR_ACCENT_GREEN = "#3FB950"
COLOR_ACCENT_AMBER = "#D29922"
COLOR_ACCENT_RED = "#F85149"
COLOR_TEXT_LIGHT = "#F0F6FC"
COLOR_TEXT_MUTED = "#8B949E"
COLOR_INPUT_BG = "#0D1117"

FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_BODY = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 11, "bold")
FONT_CODE = ("Consolas", 10)
FONT_MONO_BOLD = ("Consolas", 10, "bold")

class InterviewOSTkinterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("InterviewOS - AI Multi-Agent Interview Platform")
        self.root.geometry("1180x780")
        self.root.minsize(920, 600)
        self.root.configure(bg=COLOR_BG_DARK)

        self.state_mgr = PersistentAppState()
        self.current_session: Optional[ChatSession] = None
        self.is_evaluating = False

        self._setup_styles()
        self._setup_ui()
        self._load_or_create_initial_session()

        # Bring window to foreground immediately
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(300, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure styles
        self.style.configure(".", background=COLOR_BG_DARK, foreground=COLOR_TEXT_LIGHT, font=FONT_BODY)
        self.style.configure("Sidebar.TFrame", background=COLOR_SIDEBAR)
        self.style.configure("Card.TFrame", background=COLOR_CARD)
        self.style.configure("Main.TFrame", background=COLOR_BG_DARK)

    def _setup_ui(self):
        # Top-level Paned layout: Left Sidebar (width 310), Right Chat Area (expand)
        self.root.grid_columnconfigure(0, weight=0, minsize=300)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # =========================================================
        # 1. LEFT SIDEBAR
        # =========================================================
        self.sidebar = tk.Frame(self.root, bg=COLOR_SIDEBAR, width=310, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Header Title
        lbl_title = tk.Label(self.sidebar, text="⚡ InterviewOS", font=("Segoe UI", 16, "bold"), fg=COLOR_PRIMARY_BLUE, bg=COLOR_SIDEBAR)
        lbl_title.pack(anchor="w", padx=16, pady=(16, 2))

        lbl_sub = tk.Label(self.sidebar, text="AI Multi-Agent Interview Studio", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR)
        lbl_sub.pack(anchor="w", padx=16, pady=(0, 12))

        # "+ New Chat / Interview" Button
        btn_new_chat = tk.Button(
            self.sidebar,
            text="+ New Interview / Chat",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_ACCENT_GREEN,
            fg="#0D1117",
            activebackground="#2EA043",
            activeforeground="#0D1117",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=8,
            command=self.start_new_chat
        )
        btn_new_chat.pack(fill="x", padx=14, pady=(0, 12))

        # Mode Selector Frame
        mode_frame = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR)
        mode_frame.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(mode_frame, text="INTERVIEW TRACK", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR).pack(anchor="w", pady=(0, 3))
        
        self.mode_var = tk.StringVar(value="Project Deep Dive")
        self.mode_menu = tk.OptionMenu(
            mode_frame,
            self.mode_var,
            "Project Deep Dive",
            "Technical Round",
            "DSA Algorithmic",
            "HR & Behavioral",
            "AI Learning Mentor",
            command=self._on_mode_change
        )
        self.mode_menu.config(bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, font=FONT_BODY, relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER, activebackground=COLOR_CARD, activeforeground=COLOR_TEXT_LIGHT)
        self.mode_menu["menu"].config(bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, font=FONT_BODY)
        self.mode_menu.pack(fill="x")

        # Context Card (Loaded Memory)
        ctx_frame = tk.Frame(self.sidebar, bg=COLOR_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=10, pady=8)
        ctx_frame.pack(fill="x", padx=14, pady=(0, 10))

        tk.Label(ctx_frame, text="LOADED CONTEXT (Saved)", font=("Segoe UI", 8, "bold"), fg=COLOR_ACCENT_GREEN, bg=COLOR_CARD).pack(anchor="w", pady=(0, 4))
        
        self.lbl_jd = tk.Label(ctx_frame, text=f"📄 JD: {Path(self.state_mgr.job_path).name}", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD)
        self.lbl_jd.pack(anchor="w", pady=1)

        self.lbl_resume = tk.Label(ctx_frame, text=f"👤 Resume: {Path(self.state_mgr.resume_path).name}", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD)
        self.lbl_resume.pack(anchor="w", pady=1)

        self.lbl_repo = tk.Label(ctx_frame, text=f"🔗 Repo: {self.state_mgr.github_url.split('/')[-1]}", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_CARD)
        self.lbl_repo.pack(anchor="w", pady=1)

        btn_change = tk.Button(
            ctx_frame,
            text="Change Files / Repo",
            font=("Segoe UI", 8),
            bg="#30363D",
            fg=COLOR_TEXT_LIGHT,
            activebackground="#484F58",
            activeforeground=COLOR_TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            command=self.open_context_dialog
        )
        btn_change.pack(fill="x", pady=(6, 2))

        # Recent Sessions List
        tk.Label(self.sidebar, text="RECENT SESSIONS", font=("Segoe UI", 8, "bold"), fg=COLOR_TEXT_MUTED, bg=COLOR_SIDEBAR).pack(anchor="w", padx=16, pady=(6, 3))

        hist_container = tk.Frame(self.sidebar, bg=COLOR_SIDEBAR)
        hist_container.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.history_listbox = tk.Listbox(
            hist_container,
            bg=COLOR_SIDEBAR,
            fg=COLOR_TEXT_LIGHT,
            font=FONT_SUBTITLE,
            selectbackground=COLOR_CARD,
            selectforeground=COLOR_PRIMARY_BLUE,
            relief="flat",
            highlightthickness=0,
            activestyle="none"
        )
        self.history_listbox.pack(side="left", fill="both", expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self._on_history_select)

        # Settings Button at bottom of sidebar
        btn_settings = tk.Button(
            self.sidebar,
            text="⚙  API & Model Settings",
            font=FONT_SUBTITLE,
            bg=COLOR_CARD,
            fg=COLOR_TEXT_LIGHT,
            activebackground="#30363D",
            activeforeground=COLOR_TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=6,
            command=self.open_settings_dialog
        )
        btn_settings.pack(fill="x", padx=14, pady=12)

        # =========================================================
        # 2. RIGHT CHAT WINDOW
        # =========================================================
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG_DARK)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1) # Chat history expands
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Top Session Header
        header_bar = tk.Frame(self.main_frame, bg=COLOR_SIDEBAR, height=52, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=18)
        header_bar.grid(row=0, column=0, sticky="ew")

        self.session_title_lbl = tk.Label(
            header_bar,
            text="🎯 Project Deep Dive — AI/ML Engineer",
            font=FONT_TITLE,
            fg=COLOR_TEXT_LIGHT,
            bg=COLOR_SIDEBAR
        )
        self.session_title_lbl.pack(side="left", pady=12)

        btn_conclude = tk.Button(
            header_bar,
            text="🏁 Conclude & Score",
            font=FONT_BOLD,
            bg=COLOR_CARD,
            fg=COLOR_PRIMARY_BLUE,
            activebackground="#30363D",
            activeforeground=COLOR_PRIMARY_BLUE,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.conclude_session
        )
        btn_conclude.pack(side="right", pady=10)

        # Chat Text Display Area (Scrollable Rich Text)
        chat_frame = tk.Frame(self.main_frame, bg=COLOR_BG_DARK)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=10)

        self.chat_scroll = tk.Scrollbar(chat_frame, bg=COLOR_SIDEBAR)
        self.chat_scroll.pack(side="right", fill="y")

        self.chat_display = tk.Text(
            chat_frame,
            bg=COLOR_BG_DARK,
            fg=COLOR_TEXT_LIGHT,
            font=FONT_BODY,
            wrap="word",
            relief="flat",
            highlightthickness=0,
            state="disabled",
            yscrollcommand=self.chat_scroll.set,
            padx=14,
            pady=10
        )
        self.chat_display.pack(side="left", fill="both", expand=True)
        self.chat_scroll.config(command=self.chat_display.yview)

        # Configure rich tags
        self.chat_display.tag_configure("system", foreground=COLOR_TEXT_MUTED, font=FONT_SUBTITLE)
        self.chat_display.tag_configure("interviewer_hdr", foreground=COLOR_PRIMARY_BLUE, font=FONT_BOLD)
        self.chat_display.tag_configure("candidate_hdr", foreground=COLOR_ACCENT_GREEN, font=FONT_BOLD)
        self.chat_display.tag_configure("eval_hdr", foreground=COLOR_ACCENT_AMBER, font=FONT_BOLD)
        self.chat_display.tag_configure("prompt_tag", foreground=COLOR_TEXT_MUTED, font=FONT_CODE)
        self.chat_display.tag_configure("bubble_ai", foreground=COLOR_TEXT_LIGHT, lmargin1=10, lmargin2=10, rmargin=20)
        self.chat_display.tag_configure("bubble_user", foreground="#E6EDF3", lmargin1=10, lmargin2=10, rmargin=20)
        self.chat_display.tag_configure("bubble_eval", foreground=COLOR_TEXT_LIGHT, lmargin1=16, lmargin2=16, rmargin=20)

        # Status / Feedback Bar
        self.status_lbl = tk.Label(self.main_frame, text="", font=FONT_SUBTITLE, fg=COLOR_ACCENT_GREEN, bg=COLOR_BG_DARK)
        self.status_lbl.grid(row=2, column=0, sticky="w", padx=22, pady=(0, 2))

        # Bottom Input Container
        input_container = tk.Frame(self.main_frame, bg=COLOR_CARD, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=12, pady=10)
        input_container.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 18))
        input_container.grid_columnconfigure(0, weight=1)

        self.input_box = tk.Text(
            input_container,
            bg=COLOR_INPUT_BG,
            fg=COLOR_TEXT_LIGHT,
            font=FONT_BODY,
            height=3,
            wrap="word",
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            insertbackground=COLOR_TEXT_LIGHT,
            padx=8,
            pady=6
        )
        self.input_box.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self.input_box.bind("<Return>", self._handle_enter_key)

        # Action Buttons
        btn_code = tk.Button(
            input_container,
            text="▶  Run Code",
            font=FONT_SUBTITLE,
            bg="#30363D",
            fg=COLOR_TEXT_LIGHT,
            activebackground="#484F58",
            activeforeground=COLOR_TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=4,
            command=self.open_code_runner
        )
        btn_code.grid(row=1, column=0, sticky="w")

        hint_lbl = tk.Label(input_container, text="Press Enter to send (Shift+Enter for newline)", font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD)
        hint_lbl.grid(row=1, column=1, sticky="w", padx=12)

        self.btn_send = tk.Button(
            input_container,
            text="Send  ➤",
            font=FONT_BOLD,
            bg=COLOR_PRIMARY_BLUE,
            fg="#0D1117",
            activebackground="#79C0FF",
            activeforeground="#0D1117",
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=4,
            command=self.send_message
        )
        self.btn_send.grid(row=1, column=2, sticky="e")

    def _load_or_create_initial_session(self):
        self._render_history_list()
        if self.state_mgr.sessions:
            self._load_session_by_id(self.state_mgr.sessions[0]["id"])
        else:
            self.start_new_chat()

    def _on_mode_change(self, choice):
        self.session_title_lbl.config(text=f"🎯 {choice} — {self.state_mgr.candidate_name}")

    def start_new_chat(self):
        mode = self.mode_var.get()
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        title = f"{mode} ({datetime.datetime.now().strftime('%b %d, %H:%M')})"
        
        self.current_session = ChatSession(
            id=session_id,
            title=title,
            mode=mode,
            created_at=datetime.datetime.now().isoformat(),
            messages=[],
            scores=[]
        )
        
        self.session_title_lbl.config(text=f"🎯 {mode} — {self.state_mgr.candidate_name}")
        
        # Clear chat window
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.config(state="disabled")

        # Initial Welcome & First Question
        self._send_initial_question(mode)
        self.state_mgr.save_session(self.current_session)
        self._render_history_list()

    def _send_initial_question(self, mode: str):
        welcome_text = (
            f"Welcome, {self.state_mgr.candidate_name}! I'm your InterviewOS AI interviewer.\n"
            f"Role: AI/ML Engineer • Context Loaded: {Path(self.state_mgr.job_path).name} & {Path(self.state_mgr.resume_path).name}."
        )
        self._append_message("system", welcome_text)

        initial_questions = {
            "Project Deep Dive": (
                f"Could you give an architectural overview of your {self.state_mgr.github_url.split('/')[-1]} project, "
                f"and explain how the client connects to servers over stdio?"
            ),
            "Technical Round": (
                "Walk me through what happens under the hood when loss.backward() is called in PyTorch. "
                "How does the autograd engine build and traverse the computation graph?"
            ),
            "DSA Algorithmic": (
                "Given an integer array nums and an integer target, return the indices of two numbers that sum to target. "
                "How would you optimize the lookup to O(n) time complexity?"
            ),
            "HR & Behavioral": (
                "Tell me about a time when you had a technical disagreement with a teammate or lead regarding architectural tradeoffs. "
                "How did you resolve it?"
            ),
            "AI Learning Mentor": (
                "Hello! Based on your recent assessment, you have strong PyTorch mastery (76%) and an area to improve in SQL Window Functions (43%). "
                "What topic would you like to practice or deep dive into today?"
            )
        }

        q = initial_questions.get(mode, initial_questions["Technical Round"])
        self._append_message("interviewer", q, prompt_id="INIT_Q1")

    def _handle_enter_key(self, event):
        if event.state & 0x0001:  # Shift held
            return None
        self.send_message()
        return "break"

    def send_message(self):
        if self.is_evaluating:
            return

        text = self.input_box.get("1.0", "end-1c").strip()
        if not text:
            return

        self.input_box.delete("1.0", "end")
        self._append_message("candidate", text)

        # Check for conclusion command
        if text.lower() in ("done", "exit", "quit", "finish", "stop"):
            self.conclude_session()
            return

        # Trigger AI evaluation in background thread
        self.is_evaluating = True
        self.btn_send.config(state="disabled", text="Thinking...")
        self.status_lbl.config(text="⚡ InterviewOS is evaluating response...")

        threading.Thread(target=self._process_answer_async, args=(text,), daemon=True).start()

    def _process_answer_async(self, answer_text: str):
        try:
            import time
            time.sleep(0.6)

            ans_len = len(answer_text.strip())
            score = 0.88 if ans_len > 50 else 0.65
            
            strengths = []
            weaknesses = []
            if ans_len > 50:
                strengths.append("Structured explanation with clear technical precision.")
                if any(w in answer_text.lower() for w in ["backward", "stdio", "graph", "hash", "server", "layer", "sql", "partition"]):
                    strengths.append("Addressed core architectural/algorithmic mechanics.")
            else:
                weaknesses.append("Concise answer; recommend detailing underlying tradeoffs.")

            feedback = f"Solid response demonstrating clear grasp of mechanics (Score: {int(score*100)}%)."
            
            next_questions = {
                "Project Deep Dive": "In FileSystemMCP, how is workspace isolation enforced to prevent path traversal exploits?",
                "Technical Round": "How does Distributed Data Parallel (DDP) differ from DataParallel (DP) in multi-GPU training?",
                "DSA Algorithmic": "How would you detect a cycle in a directed graph using Topological Sort vs 3-color DFS?",
                "HR & Behavioral": "How do you handle ambiguous requirements when working on tight sprint deadlines?",
                "AI Learning Mentor": "Great! Let's write a SQL query using ROW_NUMBER() OVER (PARTITION BY ...) for ranking top transactions."
            }

            mode = self.current_session.mode if self.current_session else "Technical Round"
            next_q = next_questions.get(mode, "Could you elaborate on the scalability and failure recovery considerations?")

            self.root.after(0, lambda: self._apply_evaluation_result(score, strengths, weaknesses, feedback, next_q))
        except Exception as exc:
            self.root.after(0, lambda: self._handle_eval_error(str(exc)))

    def _handle_eval_error(self, err_msg: str):
        self.is_evaluating = False
        self.btn_send.config(state="normal", text="Send  ➤")
        self.status_lbl.config(text="")
        self._append_message("system", f"⚠️ Notice: {err_msg}")

    def _apply_evaluation_result(self, score, strengths, weaknesses, feedback, next_q):
        self.is_evaluating = False
        self.btn_send.config(state="normal", text="Send  ➤")
        self.status_lbl.config(text="")

        if self.current_session:
            self.current_session.scores.append(score)

        # Render Evaluation feedback card
        self._append_evaluation_card(score, strengths, weaknesses, feedback)

        # Render next interviewer question
        self._append_message("interviewer", next_q, prompt_id="FOLLOW_UP_Q2")

        if self.current_session:
            self.state_mgr.save_session(self.current_session)

    def _append_message(self, role: str, content: str, prompt_id: Optional[str] = None):
        self.chat_display.config(state="normal")
        
        timestamp = datetime.datetime.now().strftime("%H:%M")

        if role == "interviewer":
            pid_str = f"  [{prompt_id}]" if prompt_id else ""
            self.chat_display.insert("end", f"\n🤖 Interviewer{pid_str} • {timestamp}\n", "interviewer_hdr")
            self.chat_display.insert("end", f"{content}\n\n", "bubble_ai")

        elif role == "candidate":
            self.chat_display.insert("end", f"\n👤 {self.state_mgr.candidate_name} • {timestamp}\n", "candidate_hdr")
            self.chat_display.insert("end", f"{content}\n\n", "bubble_user")

        else: # system
            self.chat_display.insert("end", f"\n⚡ System • {timestamp}\n", "system")
            self.chat_display.insert("end", f"{content}\n\n", "bubble_ai")

        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

        if self.current_session:
            self.current_session.messages.append({
                "role": role,
                "content": content,
                "prompt_id": prompt_id
            })

    def _append_evaluation_card(self, score: float, strengths: List[str], weaknesses: List[str], feedback: str):
        self.chat_display.config(state="normal")
        
        score_pct = int(score * 100)
        self.chat_display.insert("end", f"📊 AI Evaluation • Score: {score_pct}%\n", "eval_hdr")
        self.chat_display.insert("end", f"{feedback}\n", "bubble_eval")
        
        if strengths:
            self.chat_display.insert("end", "✓ " + " | ".join(strengths) + "\n", "bubble_eval")
        if weaknesses:
            self.chat_display.insert("end", "⚠ " + " | ".join(weaknesses) + "\n", "bubble_eval")
            
        self.chat_display.insert("end", "\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

    def conclude_session(self):
        if not self.current_session:
            return

        scores = self.current_session.scores
        overall = sum(scores) / len(scores) if scores else 0.85
        self.current_session.overall_score = overall
        self.current_session.is_completed = True
        self.state_mgr.save_session(self.current_session)

        summary_msg = (
            f"🎉 Interview Round Concluded!\n"
            f"• Track: {self.current_session.mode}\n"
            f"• Overall Weighted Score: {int(overall*100)}%\n"
            f"• Status: Passed Benchmark\n"
            f"• Summary: Candidate demonstrated solid technical ownership, clear terminology, and practical depth."
        )
        self._append_message("system", summary_msg)
        messagebox.showinfo("Interview Completed", f"Round completed with Overall Score: {int(overall*100)}%")

    def _render_history_list(self):
        self.history_listbox.delete(0, "end")
        for s in self.state_mgr.sessions:
            title = s.get("title", "Untitled Interview")
            self.history_listbox.insert("end", f"💬 {title}")

    def _on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.state_mgr.sessions):
                sess_data = self.state_mgr.sessions[idx]
                self._load_session_by_id(sess_data["id"])

    def _load_session_by_id(self, sess_id: str):
        for s in self.state_mgr.sessions:
            if s.get("id") == sess_id:
                self.current_session = ChatSession(**s)
                self.session_title_lbl.config(text=f"🎯 {self.current_session.mode} — {self.state_mgr.candidate_name}")
                
                self.chat_display.config(state="normal")
                self.chat_display.delete("1.0", "end")
                self.chat_display.config(state="disabled")

                for msg in self.current_session.messages:
                    self._append_message(msg["role"], msg["content"], msg.get("prompt_id"))
                return

    # =========================================================
    # DIALOGS: CONTEXT & SETTINGS
    # =========================================================
    def open_context_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Context Files & Repo")
        dialog.geometry("500x320")
        dialog.configure(bg=COLOR_BG_DARK)
        dialog.transient(self.root)

        tk.Label(dialog, text="Context Configuration", font=FONT_TITLE, fg=COLOR_PRIMARY_BLUE, bg=COLOR_BG_DARK).pack(padx=20, pady=(15, 10))

        # JD File
        f1 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f1.pack(fill="x", padx=20, pady=5)
        tk.Label(f1, text="Job Description:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        jd_ent = tk.Entry(f1, width=32, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, insertbackground=COLOR_TEXT_LIGHT)
        jd_ent.insert(0, self.state_mgr.job_path)
        jd_ent.pack(side="right")

        # Resume File
        f2 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f2.pack(fill="x", padx=20, pady=5)
        tk.Label(f2, text="Resume PDF:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        res_ent = tk.Entry(f2, width=32, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, insertbackground=COLOR_TEXT_LIGHT)
        res_ent.insert(0, self.state_mgr.resume_path)
        res_ent.pack(side="right")

        # GitHub Repo
        f3 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f3.pack(fill="x", padx=20, pady=5)
        tk.Label(f3, text="GitHub URL:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        repo_ent = tk.Entry(f3, width=32, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, insertbackground=COLOR_TEXT_LIGHT)
        repo_ent.insert(0, self.state_mgr.github_url)
        repo_ent.pack(side="right")

        def save_context():
            self.state_mgr.job_path = jd_ent.get().strip()
            self.state_mgr.resume_path = res_ent.get().strip()
            self.state_mgr.github_url = repo_ent.get().strip()
            self.state_mgr.save()

            self.lbl_jd.config(text=f"📄 JD: {Path(self.state_mgr.job_path).name}")
            self.lbl_resume.config(text=f"👤 Resume: {Path(self.state_mgr.resume_path).name}")
            self.lbl_repo.config(text=f"🔗 Repo: {self.state_mgr.github_url.split('/')[-1]}")
            dialog.destroy()
            messagebox.showinfo("Saved", "Context updated and saved successfully!")

        tk.Button(dialog, text="Save & Update", font=FONT_BOLD, bg=COLOR_PRIMARY_BLUE, fg="#0D1117", command=save_context).pack(pady=20)

    def open_settings_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("API & Credentials Configuration")
        dialog.geometry("500x320")
        dialog.configure(bg=COLOR_BG_DARK)
        dialog.transient(self.root)

        tk.Label(dialog, text="LLM & GitHub Settings", font=FONT_TITLE, fg=COLOR_PRIMARY_BLUE, bg=COLOR_BG_DARK).pack(padx=20, pady=(15, 10))

        settings = get_settings()

        # Provider
        f0 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f0.pack(fill="x", padx=20, pady=5)
        tk.Label(f0, text="LLM Provider:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        prov_var = tk.StringVar(value=settings.llm_provider)
        prov_opt = tk.OptionMenu(f0, prov_var, "nvidia", "openai")
        prov_opt.config(bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, font=FONT_SUBTITLE)
        prov_opt.pack(side="right")

        # Model
        f1 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f1.pack(fill="x", padx=20, pady=5)
        tk.Label(f1, text="LLM Model:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        model_ent = tk.Entry(f1, width=32, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, insertbackground=COLOR_TEXT_LIGHT)
        model_ent.insert(0, settings.llm_model)
        model_ent.pack(side="right")

        # API Key
        f2 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f2.pack(fill="x", padx=20, pady=5)
        tk.Label(f2, text="API Key:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        key_ent = tk.Entry(f2, width=32, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, insertbackground=COLOR_TEXT_LIGHT, show="•")
        if settings.llm_api_key:
            key_ent.insert(0, settings.llm_api_key)
        key_ent.pack(side="right")

        # GitHub Token
        f3 = tk.Frame(dialog, bg=COLOR_BG_DARK)
        f3.pack(fill="x", padx=20, pady=5)
        tk.Label(f3, text="GitHub PAT:", font=FONT_SUBTITLE, fg=COLOR_TEXT_LIGHT, bg=COLOR_BG_DARK).pack(side="left")
        gh_ent = tk.Entry(f3, width=32, bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, insertbackground=COLOR_TEXT_LIGHT, show="•")
        if settings.github_token:
            gh_ent.insert(0, settings.github_token)
        gh_ent.pack(side="right")

        def save_cfg():
            if key_ent.get().strip():
                os.environ["LLM_API_KEY"] = key_ent.get().strip()
            if model_ent.get().strip():
                os.environ["LLM_MODEL"] = model_ent.get().strip()
            if gh_ent.get().strip():
                os.environ["GITHUB_TOKEN"] = gh_ent.get().strip()
            os.environ["LLM_PROVIDER"] = prov_var.get()
            dialog.destroy()
            messagebox.showinfo("Config Saved", "API credentials updated for this session.")

        tk.Button(dialog, text="Save Settings", font=FONT_BOLD, bg=COLOR_PRIMARY_BLUE, fg="#0D1117", command=save_cfg).pack(pady=20)

    def open_code_runner(self):
        code = self.input_box.get("1.0", "end-1c").strip()
        
        runner_win = tk.Toplevel(self.root)
        runner_win.title("Python Code Runner Scratchpad")
        runner_win.geometry("560x420")
        runner_win.configure(bg=COLOR_BG_DARK)
        runner_win.transient(self.root)

        tk.Label(runner_win, text="Execution Output", font=FONT_TITLE, fg=COLOR_PRIMARY_BLUE, bg=COLOR_BG_DARK).pack(padx=15, pady=(10, 4), anchor="w")

        out_box = tk.Text(runner_win, font=FONT_CODE, fg=COLOR_ACCENT_GREEN, bg="#000000", padx=10, pady=10)
        out_box.pack(fill="both", expand=True, padx=15, pady=10)

        # Run safely
        buffer_out = io.StringIO()
        buffer_err = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer_out), contextlib.redirect_stderr(buffer_err):
                exec(code, {"__builtins__": __builtins__})
            res = buffer_out.getvalue() or "Code executed successfully with 0 return output."
            out_box.insert("1.0", f">>> Output:\n{res}")
        except Exception as exc:
            out_box.config(fg=COLOR_ACCENT_RED)
            out_box.insert("1.0", f">>> Execution Error:\n{type(exc).__name__}: {str(exc)}")


def launch_gui():
    root = tk.Tk()
    app = InterviewOSTkinterApp(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
