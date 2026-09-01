import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

STATE_FILE = Path("data/gui_state.json")

class ChatSession(BaseModel):
    id: str
    title: str
    mode: str
    created_at: str
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    scores: List[float] = Field(default_factory=list)
    overall_score: Optional[float] = None
    is_completed: bool = False

class PersistentAppState:
    def __init__(self):
        self.candidate_name: str = "Omsai Ramachandran"
        self.candidate_email: str = "omsai@example.com"
        self.job_path: str = "data/input/job_descriptions/sample_jd.pdf"
        self.resume_path: str = "data/input/resumes/sample_resume.pdf"
        self.github_url: str = "https://github.com/omsaichand35/MCP"
        self.difficulty: str = "medium"
        self.duration_minutes: int = 30
        self.sessions: List[Dict[str, Any]] = []
        self.skill_mastery: Dict[str, int] = {
            "Python": 82,
            "ML": 71,
            "PyTorch": 76,
            "SQL": 43,
            "Docker": 51,
            "Algorithms": 78,
            "System Design": 85,
        }
        self.load()

    def load(self):
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                self.candidate_name = data.get("candidate_name", self.candidate_name)
                self.candidate_email = data.get("candidate_email", self.candidate_email)
                self.job_path = data.get("job_path", self.job_path)
                self.resume_path = data.get("resume_path", self.resume_path)
                self.github_url = data.get("github_url", self.github_url)
                self.difficulty = data.get("difficulty", self.difficulty)
                self.duration_minutes = data.get("duration_minutes", self.duration_minutes)
                self.sessions = data.get("sessions", [])
                if "skill_mastery" in data:
                    self.skill_mastery.update(data["skill_mastery"])
            except Exception as e:
                print(f"[State] Could not load state: {e}")

    def save(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "job_path": self.job_path,
            "resume_path": self.resume_path,
            "github_url": self.github_url,
            "difficulty": self.difficulty,
            "duration_minutes": self.duration_minutes,
            "sessions": self.sessions[-20:], # keep recent 20
            "skill_mastery": self.skill_mastery,
        }
        try:
            STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[State] Could not save state: {e}")

    def save_session(self, session: ChatSession):
        # Update or add session
        for i, s in enumerate(self.sessions):
            if s.get("id") == session.id:
                self.sessions[i] = session.model_dump()
                self.save()
                return
        self.sessions.insert(0, session.model_dump())
        self.save()
