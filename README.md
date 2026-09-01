# InterviewOS ⚡

**InterviewOS** is an autonomous multi-agent AI technical interviewing and candidate mentoring platform. It orchestrates intelligent technical assessments across Online Assessments (OA), Technical Deep Dives, DSA / Algorithmic challenges, Project Code Reviews (via GitHub AST analysis), and HR/Behavioral interviews.

---

## 🌟 Key Features

- **Multi-Round Interview Engine**:
  - **Online Assessment (OA)**: Timed conceptual & coding assessments with automated grading.
  - **Technical Interview**: Deep dive into framework internals (PyTorch, Distributed Systems, ML architectures).
  - **DSA / Algorithmic Round**: Live problem formulation, approach validation, complexity analysis, and code evaluation.
  - **Project Deep Dive (GitHub)**: Autonomous repository ingestion, file hierarchy scanning, and architectural probing via GitHub API.
  - **HR & Behavioral Round**: Competency-based situational inquiries evaluated against role requirements.
  - **AI Learning Workspace / Mentor**: Personalized feedback, skill mastery tracking, and targeted learning recommendations.

- **Enterprise-Grade AI Architecture**:
  - Structured output parsing with `json-repair` fault tolerance.
  - Pluggable LLM providers (NVIDIA NIM, OpenAI).
  - Deterministic evaluation pipelines and candidate ranking engine.

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/omsaichand35/Interview.git
cd Interview

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
LLM_PROVIDER=nvidia
LLM_MODEL=nvidia/nemotron-3-super-120b-a12b
LLM_API_KEY=your_nvidia_or_openai_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

### 3. One-Click Interactive Menu Launcher

Launch all interviews, assessments, and tools interactively from a single terminal menu:

```bash
# Windows
.\run.bat
# or
powershell -ExecutionPolicy Bypass -File .\run.ps1

# Linux / macOS
python3 scripts/menu.py
```

---

### 4. Direct Runner Scripts (`scripts/`)

| Script | Purpose |
| :--- | :--- |
| **`scripts/run_project_interview.ps1`** | Launch Project Deep Dive Interview (GitHub AST parsing) |
| **`scripts/run_technical_interview.ps1`** | Launch Technical Framework & Architecture Round |
| **`scripts/run_dsa_interview.ps1`** | Launch DSA Algorithmic Problem & Coding Round |
| **`scripts/run_hr_interview.ps1`** | Launch HR & Behavioral Interview |
| **`scripts/run_oa.ps1`** | Launch timed Online Assessment (OA) |
| **`scripts/run_mentor.ps1`** | Launch AI Learning Mentor & Roadmap Agent |
| **`scripts/run_project_analyze.ps1`** | Run standalone GitHub repository code analysis |
| **`scripts/run_all_tests.ps1`** | Run full pytest test suite |

*(Equivalent `.sh` scripts are also provided in `scripts/` for Linux / macOS environments)*

---

### 5. CLI Interview Commands

```bash
# Run Project Deep Dive
python -m interviewos.cli interview --type project --job "data/input/job_descriptions/sample_jd.pdf" --name "Candidate Name" --email "candidate@example.com" --github "https://github.com/username/repo"

# Run Technical Round
python -m interviewos.cli interview --type technical --job "data/input/job_descriptions/sample_jd.pdf" --name "Candidate Name" --email "candidate@example.com"

# Run OA Assessment
python -m interviewos.cli oa --job "data/input/job_descriptions/sample_jd.pdf" --name "Candidate Name" --email "candidate@example.com" --questions 5 --duration 20

# Run AI Learning Mentor
python -m interviewos.cli mentor --resume "data/input/resumes/sample_resume.pdf" --job "data/input/job_descriptions/sample_jd.pdf"
```

---

## 🧪 Testing

Run the full pytest suite:

```bash
pytest tests/ -q
```

---

## 📁 Repository Structure

```
interviewos/
├── data/                       # Sample JDs, Resumes, and evaluation artifacts
├── src/interviewos/
│   ├── cli/                    # CLI commands and entry point
│   ├── config/                 # Pydantic settings and path management
│   ├── core/                   # PDF loaders and document ingestion
│   ├── interview/              # Multi-agent interview engine & strategies
│   │   ├── strategies/         # DSA, Technical, HR, Managerial, Project
│   │   ├── project/            # GitHub client and repository agent
│   │   └── scoring/            # Rubric scoring & evaluation models
│   ├── llm/                    # Structured output clients and repair
│   ├── learning/               # Candidate skill roadmap & gap analysis
│   ├── mentor/                 # Adaptive learning tutor & practice agent
│   └── orchestrator/           # Hiring pipeline & ranking engine
└── tests/                      # Unit and integration test suite
```

---

## 📄 License

MIT License.
