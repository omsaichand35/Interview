from pathlib import Path
import uuid

from interviewos.analysis import (
    JobAnalyzer,
    ResumeAnalyzer,
    SkillGapAnalyzer,
)
from interviewos.config import (
    get_project_paths,
    get_settings,
)
from interviewos.ingestion import PDFLoader
from interviewos.llm import create_llm_client
from interviewos.models import JobProfile
from interviewos.mentor import Mentor
from interviewos.planning import LearningPlanner
from interviewos.rag import (
    DocumentProcessor,
    QdrantVectorStore,
    RAGPipeline,
    SentenceTransformerEmbeddings,
    TextChunker,
)

from .display import (
    print_job,
    print_learning_plan,
    print_resume,
    print_skill_gaps,
)
from ..assessment import TerminalOARunner, AssessmentBlueprintGenerator, OAEngine
from ..assessment.candidate_store import CandidateStore
from ..assessment.candidates import CandidateManager


class InterviewOSApplication:
    """
    Terminal application for InterviewOS Phase 1.

    This class coordinates existing application services.
    It does not contain analysis or RAG business logic.
    """

    def __init__(
            self,
            resume_path: Path | None,
            job_path: Path,
    ) -> None:

        self.resume_path = (
            Path(resume_path)
            if resume_path
            else None
        )
        self.job_path = Path(job_path)

        self.settings = get_settings()
        self.paths = get_project_paths()

        self.llm = create_llm_client()

        self.pdf_loader = PDFLoader()

        self.resume = None
        self.job = None
        self.skill_gap_report = None
        self.learning_plan = None
        self.mentor = None
        self.rag = None

    async def analyze_documents_async(self) -> None:
        """Analyze resume and job description asynchronously."""

        if self.resume_path:
            print("Loading resume...")
            resume_document = self.pdf_loader.load(self.resume_path)
            print("Analyzing resume...")
            self.resume = await ResumeAnalyzer(self.llm).analyze_async(resume_document)
            print_resume(self.resume)
        else:
            print("No resume provided, skipping resume analysis...")

        print("Loading job description...")
        job_document = self.pdf_loader.load(self.job_path)
        print("Analyzing job description...")
        self.job = await JobAnalyzer(self.llm).analyze_async(job_document)
        print_job(self.job)

    def analyze_documents(self) -> None:
        """Analyze resume and job description (sync, for Phase 1 mentor flow)."""

        if self.resume_path:
            print("Loading resume...")
            resume_document = self.pdf_loader.load(self.resume_path)
            print("Analyzing resume...")
            self.resume = ResumeAnalyzer(self.llm).analyze(resume_document)
            print_resume(self.resume)
        else:
            print("No resume provided, skipping resume analysis...")

        print("Loading job description...")
        job_document = self.pdf_loader.load(self.job_path)
        print("Analyzing job description...")
        self.job = JobAnalyzer(self.llm).analyze(job_document)
        print_job(self.job)

    def create_learning_plan(self) -> None:
        """Generate the candidate's learning plan."""

        if self.resume is None:
            raise RuntimeError(
                "Resume analysis has not been completed."
            )

        if self.job is None:
            raise RuntimeError(
                "Job analysis has not been completed."
            )

        analyzer = SkillGapAnalyzer()

        self.skill_gap_report = analyzer.analyze(
            resume=self.resume,
            job=self.job,
        )

        print_skill_gaps(
            self.skill_gap_report
        )

        from interviewos.planning.plan_generator import PlanGenerator
        from interviewos.planning.plan_manager import PlanManager
        from interviewos.storage.plan_repository import JSONPlanRepository
        
        generator = PlanGenerator(self.llm)

        self.learning_plan = generator.generate_initial_plan(
            resume=self.resume,
            job=self.job,
            skill_gap_report=self.skill_gap_report,
        )
        
        # Save plan and get recommendation
        repo = JSONPlanRepository(self.paths.plans)
        manager = PlanManager(repository=repo)
        manager.save_plan(self.learning_plan)

        print_learning_plan(
            self.learning_plan
        )

    def initialize_rag(self) -> None:
        """Initialize the knowledge retrieval system."""

        embeddings = SentenceTransformerEmbeddings(
            self.settings.embeddings_model
        )

        store = QdrantVectorStore(
            path=self.paths.vectorstore
        )

        self.rag = RAGPipeline(
            document_processor=DocumentProcessor(),
            chunker=TextChunker(),
            embeddings=embeddings,
            vector_store=store,
            llm=self.llm,
        )

    def initialize_mentor(self) -> None:
        """Initialize the adaptive mentor."""

        if self.rag is None:
            raise RuntimeError(
                "RAG has not been initialized."
            )

        self.mentor = Mentor(
            llm=self.llm,
            rag=self.rag,
            learning_plan=self.learning_plan,
        )

    def run(
        self,
        knowledge_directory: Path | None = None,
    ) -> None:
        """Run the complete Phase 1 startup sequence."""

        self.analyze_documents()

        self.create_learning_plan()

        print("\nInitializing RAG...")

        self.initialize_rag()

        if knowledge_directory:
            print(
                f"Indexing knowledge from: "
                f"{knowledge_directory}"
            )

            count = self.rag.ingest_directory(
                knowledge_directory
            )

            print(
                f"Indexed {count} chunks."
            )

        self.initialize_mentor()

        self.mentor_loop()

    def mentor_loop(self) -> None:
        """Start the terminal mentor."""

        if self.mentor is None:
            raise RuntimeError(
                "Mentor has not been initialized."
            )

        print()
        print("=" * 70)
        print("INTERVIEWOS MENTOR")
        print("=" * 70)

        print(
            "\nYour personalized mentor is ready."
        )

        print(
            "Type /help for commands or /quit to exit."
        )

        while True:
            try:
                message = input("\nYou > ").strip()

            except (KeyboardInterrupt, EOFError):
                print("\nExiting InterviewOS.")
                break

            if not message:
                continue

            if message == "/quit":
                print("Goodbye.")
                break

            if message == "/help":
                from .display import print_help

                print_help()
                continue

            if message == "/state":
                print(
                    self.mentor.get_state()
                    .model_dump_json(
                        indent=2
                    )
                )
                continue

            if message.startswith("/practice"):
                topic = message[
                    len("/practice"):
                ].strip()

                if not topic:
                    topic = (
                        self.mentor
                        .get_state()
                        .current_topic
                        or "interview fundamentals"
                    )

                question = self.mentor.practice(
                    topic
                )

                print(
                    f"\nMentor > {question.question}"
                )

                continue

            if message == "/review":
                response = self.mentor.interact(
                    "Review my weakest topic."
                )

                print(
                    f"\nMentor > {response}"
                )

                continue

            try:
                response = self.mentor.interact(
                    message
                )

                print(
                    f"\nMentor > {response}"
                )

            except Exception as exc:
                print(
                    f"\nError: {exc}"
                )

    def create_oa_engine(self) -> OAEngine:
        from interviewos.assessment import OAEngine
        from interviewos.assessment.question_generator import QuestionGenerator
        from interviewos.assessment.evaluator import AssessmentEvaluator
        from interviewos.assessment.scoring import AssessmentScorer
        from interviewos.assessment.question_validator import QuestionValidator
        from interviewos.assessment.semantic_validation import SemanticQuestionValidator
        from interviewos.assessment.question_bank import QuestionBank
        from interviewos.assessment.question_bank_store import QuestionBankStore
        from interviewos.assessment.session import AssessmentSessionManager
        from interviewos.assessment.persistence import AssessmentSessionStore
        
        qb_store = QuestionBankStore(self.paths.data / "question_bank")
        qb = QuestionBank(qb_store)
        
        session_store = AssessmentSessionStore(self.paths.sessions)
        session_manager = AssessmentSessionManager(question_bank=qb, store=session_store)

        return OAEngine(
            question_generator=QuestionGenerator(self.llm),
            evaluator=AssessmentEvaluator(),
            scorer=AssessmentScorer(),
            question_validator=QuestionValidator(),
            semantic_validator=SemanticQuestionValidator(self.llm),
            question_bank=qb,
            session_manager=session_manager,
        )

    async def run_oa(
        self,
        candidate_name: str,
        candidate_email: str,
        total_questions: int,
        duration_minutes: int,
        threshold: float,
        topics: str | None = None,
        job: JobProfile | None = None,
    ) -> float:
        """Run a terminal objective assessment."""

        if not self.job_path.exists():
            raise FileNotFoundError(
                f"Job description not found: "
                f"{self.job_path}"
            )

        if total_questions <= 0:
            raise ValueError(
                "Number of questions must be greater than zero."
            )

        if duration_minutes <= 0:
            raise ValueError(
                "Duration must be greater than zero."
            )

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "Threshold must be between 0 and 1."
            )

        print()
        print("=" * 70)
        print("INTERVIEWOS OBJECTIVE ASSESSMENT")
        print("=" * 70)

        if job is None:
            print("\nAnalyzing job description...")

            job_document = self.pdf_loader.load(
                self.job_path
            )

            job = await JobAnalyzer(
                self.llm
            ).analyze_async(
                job_document
            )

        print(
            f"\nRole: {job.title}"
        )

        if topics:
            print(f"Custom Topics: {topics}")

        print(
            "\nGenerating assessment blueprint..."
        )

        blueprint = await (
            AssessmentBlueprintGenerator(
                self.llm
            ).generate(
                job=job,
                total_questions=total_questions,
                duration_minutes=duration_minutes,
                topics=topics,
            )
        )

        print(
            f"Questions: "
            f"{blueprint.total_questions}"
        )

        print(
            f"Duration: "
            f"{blueprint.duration_minutes} minutes"
        )

        print(
            "\nCreating candidate..."
        )

        candidate_store = CandidateStore(
            self.paths.candidates
        )

        candidate_manager = CandidateManager(
            candidate_store
        )

        candidate = candidate_manager.create(
            name=candidate_name,
            email=candidate_email,
        )

        print(
            f"Candidate ID: "
            f"{candidate.id}"
        )

        engine = self.create_oa_engine()

        print(
            "\nGenerating and validating questions..."
        )

        session = await engine.create_session(
            blueprint=blueprint,
            job=job,
            candidate_id=candidate.id,
        )

        print(
            f"Assessment session: "
            f"{session.id}"
        )

        print(
            "\nStarting assessment..."
        )

        runner = TerminalOARunner(
            engine
        )

        result = runner.run(
            session.id
        )

        print(
            "\nFinal status: "
            + (
                "PASSED"
                if result.score >= threshold
                else "NOT PASSED"
            )
        )
        
        return result.score

    async def run_interview(
        self,
        interview_type: str,
        candidate_name: str,
        candidate_email: str,
        duration_minutes: int,
        difficulty: str,
        job: JobProfile | None = None,
        github_url: str | None = None,
    ) -> float | None:
        """Run a terminal interview."""
        
        from interviewos.interview.engine import InterviewEngine
        from interviewos.interview.session import InterviewSession, InterviewType
        from interviewos.interview.state import InterviewState, InterviewEvent
        from interviewos.interview.state_machine import InterviewStateMachine
        from interviewos.interview.brain import InterviewBrain
        from interviewos.interview.interviewer import Interviewer
        from interviewos.interview.context_builder import InterviewContextBuilder
        
        from interviewos.cli.tui import (
            print_round_header,
            print_question_card,
            prompt_candidate_answer,
            show_thinking_spinner,
            print_evaluation_card,
            print_final_scorecard,
        )

        if job is None:
            with show_thinking_spinner("Analyzing Job Description..."):
                job_document = self.pdf_loader.load(self.job_path)
                job = await JobAnalyzer(self.llm).analyze_async(job_document)
        
        if interview_type == "dsa":
            from interviewos.interview.strategies.dsa import DSAInterviewStrategy, DSAProblemGenerator
            strategy = DSAInterviewStrategy()
            
            session = InterviewSession(
                id=str(uuid.uuid4()),
                interview_type=InterviewType.DSA,
                candidate_id=candidate_name,
                job_id="job",
                duration_minutes=duration_minutes
            )
            
            engine = InterviewEngine(
                interviewer=Interviewer(self.llm),
                state_machine=InterviewStateMachine(),
                brain=InterviewBrain(self.llm, Interviewer(self.llm), strategy)
            )
            
            engine.start(session)
            print_round_header("DSA Algorithmic", job.title, candidate_name, duration_minutes)
            
            generator = DSAProblemGenerator(self.llm)
            with show_thinking_spinner("Formulating customized DSA problem..."):
                problem = await generator.generate(job, difficulty, [])
            session.current_dsa_problem = problem
            session.dsa_problems.append(problem)
            
            engine.state_machine.transition(session, InterviewEvent.PRESENT_PROBLEM)
            engine.state_machine.transition(session, InterviewEvent.MOVE_TO_UNDERSTANDING)
            engine.ask(session, f"**Problem:** {problem.title}\n\n{problem.statement}\n\nBefore coding, explain your high-level algorithmic approach and time/space complexity tradeoffs.")
            
            while session.state not in (InterviewState.CLOSING, InterviewState.COMPLETED):
                print_question_card(session.questions_asked + 1, 5, session.current_question, competency="Algorithmic Formulation & Coding")
                answer = prompt_candidate_answer()
                
                if not answer or answer.lower() in ('quit', 'exit', 'done', 'finish', 'stop'):
                    print("\n[Candidate requested to conclude interview.]")
                    break
                
                context = InterviewContextBuilder().build(job=job, session=session)
                with show_thinking_spinner("Evaluating algorithmic solution & complexity..."):
                    decision = await engine.process_answer(context, answer)
                
                if session.scores:
                    latest = session.scores[-1]
                    print_evaluation_card(
                        score=latest.score,
                        strengths=latest.strengths,
                        weaknesses=latest.weaknesses,
                        feedback=f"Assessed against {job.title} DSA benchmark."
                    )

                if session.questions_asked >= 5 or session.is_time_up:
                    engine.state_machine.transition(session, InterviewEvent.END)
                    break
                
            engine.close(session)
            
            overall_score = sum(s.score for s in session.scores) / len(session.scores) if session.scores else 0.85
            print_final_scorecard("DSA Algorithmic", candidate_name, overall_score, assessments=session.scores)
            return overall_score
            
        elif interview_type == "technical":
            from interviewos.interview.strategies.technical import TechnicalInterviewStrategy, TechnicalBlueprintGenerator, TechnicalQuestionGenerator
            strategy = TechnicalInterviewStrategy()
            
            session = InterviewSession(
                id=str(uuid.uuid4()),
                interview_type=InterviewType.TECHNICAL,
                candidate_id=candidate_name,
                job_id="job",
                duration_minutes=duration_minutes
            )
            
            engine = InterviewEngine(
                interviewer=Interviewer(self.llm),
                state_machine=InterviewStateMachine(),
                brain=InterviewBrain(self.llm, Interviewer(self.llm), strategy)
            )
            
            with show_thinking_spinner("Generating Technical interview blueprint..."):
                blueprint_generator = TechnicalBlueprintGenerator(self.llm)
                blueprint = await blueprint_generator.generate(job)
            session.technical_blueprint = blueprint
            
            engine.start(session)
            print_round_header("Technical Architecture", job.title, candidate_name, duration_minutes, extra_info={"🧠 Prioritized Competencies": str(len(blueprint.competencies))})
            
            question_generator = TechnicalQuestionGenerator(self.llm)
            
            while session.state not in (InterviewState.CLOSING, InterviewState.COMPLETED):
                if session.state == InterviewState.QUESTIONING:
                    target_competency = blueprint.competencies[0].name
                    for comp in blueprint.competencies:
                        if comp.name not in session.covered_competencies:
                            target_competency = comp.name
                            break
                            
                    target_topic = "general"
                    transcript_text = "\n".join(f"{msg.role}: {msg.content}" for msg in session.transcript)
                    
                    with show_thinking_spinner(f"Generating question for {target_competency}..."):
                        question = await question_generator.generate(job, target_competency, target_topic, difficulty, transcript_text)
                    engine.ask(session, question.question_text)
                
                print_question_card(session.questions_asked + 1, 5, session.current_question, competency=target_competency)
                answer = prompt_candidate_answer()
                
                if not answer or answer.lower() in ('quit', 'exit', 'done', 'finish', 'stop'):
                    print("\n[Candidate requested to conclude interview.]")
                    break
                
                context = InterviewContextBuilder().build(job=job, session=session)
                with show_thinking_spinner("Evaluating technical depth & conceptual precision..."):
                    decision = await engine.process_answer(context, answer)
                
                if session.scores:
                    latest = session.scores[-1]
                    print_evaluation_card(
                        score=latest.score,
                        strengths=latest.strengths,
                        weaknesses=latest.weaknesses,
                        feedback=f"Evaluated on {target_competency} depth."
                    )
                
                if session.questions_asked >= 5 or session.is_time_up:
                    engine.state_machine.transition(session, InterviewEvent.END)
                    break
                    
            engine.close(session)
            overall_score = sum(s.score for s in session.scores) / len(session.scores) if session.scores else 0.85
            print_final_scorecard("Technical Architecture", candidate_name, overall_score, assessments=session.scores)
            return overall_score
            
        elif interview_type == "hr":
            from interviewos.interview.strategies.hr import HRInterviewStrategy, HRBlueprintGenerator, HRQuestionGenerator
            strategy = HRInterviewStrategy()
            
            session = InterviewSession(
                id=str(uuid.uuid4()),
                interview_type=InterviewType.HR,
                candidate_id=candidate_name,
                job_id="job",
                duration_minutes=duration_minutes
            )
            
            engine = InterviewEngine(
                interviewer=Interviewer(self.llm),
                state_machine=InterviewStateMachine(),
                brain=InterviewBrain(self.llm, Interviewer(self.llm), strategy)
            )
            
            with show_thinking_spinner("Generating HR interview blueprint..."):
                blueprint_generator = HRBlueprintGenerator(self.llm)
                blueprint = await blueprint_generator.generate(job)
            session.hr_blueprint = blueprint
            
            engine.start(session)
            print_round_header("HR & Behavioral", job.title, candidate_name, duration_minutes, extra_info={"🤝 Prioritized Behaviors": str(len(blueprint.competencies))})
            
            question_generator = HRQuestionGenerator(self.llm)
            
            while session.state not in (InterviewState.CLOSING, InterviewState.COMPLETED):
                if session.state == InterviewState.QUESTIONING:
                    target_competency = blueprint.competencies[0].name
                    for comp in blueprint.competencies:
                        if comp.name not in session.covered_competencies:
                            target_competency = comp.name
                            break
                            
                    transcript_text = "\n".join(f"{msg.role}: {msg.content}" for msg in session.transcript)
                    with show_thinking_spinner(f"Generating question for {target_competency}..."):
                        question = await question_generator.generate(job, target_competency, transcript_text)
                    engine.ask(session, question.question_text)
                
                print_question_card(session.questions_asked + 1, 5, session.current_question, competency=target_competency)
                answer = prompt_candidate_answer()
                
                if not answer or answer.lower() in ('quit', 'exit', 'done', 'finish', 'stop'):
                    print("\n[Candidate requested to conclude interview.]")
                    break
                
                context = InterviewContextBuilder().build(job=job, session=session)
                with show_thinking_spinner("Evaluating behavioral responses & culture fit..."):
                    decision = await engine.process_answer(context, answer)
                
                if session.scores:
                    latest = session.scores[-1]
                    print_evaluation_card(
                        score=latest.score,
                        strengths=latest.strengths,
                        weaknesses=latest.weaknesses,
                        feedback=f"Assessed on {target_competency} ownership."
                    )
                
                if session.questions_asked >= 5 or session.is_time_up:
                    engine.state_machine.transition(session, InterviewEvent.END)
                    break
                    
            engine.close(session)
            overall_score = sum(s.score for s in session.scores) / len(session.scores) if session.scores else 0.85
            print_final_scorecard("HR & Behavioral", candidate_name, overall_score, assessments=session.scores)
            return overall_score
            
        elif interview_type == "managerial":
            from interviewos.interview.strategies.managerial import ManagerialInterviewStrategy, ManagerialBlueprintGenerator, ManagerialQuestionGenerator
            strategy = ManagerialInterviewStrategy()
            
            session = InterviewSession(
                id=str(uuid.uuid4()),
                interview_type=InterviewType.MANAGERIAL,
                candidate_id=candidate_name,
                job_id="job",
                duration_minutes=duration_minutes
            )
            
            engine = InterviewEngine(
                interviewer=Interviewer(self.llm),
                state_machine=InterviewStateMachine(),
                brain=InterviewBrain(self.llm, Interviewer(self.llm), strategy)
            )
            
            with show_thinking_spinner("Generating Managerial interview blueprint..."):
                blueprint_generator = ManagerialBlueprintGenerator(self.llm)
                blueprint = await blueprint_generator.generate(job)
            session.managerial_blueprint = blueprint
            
            engine.start(session)
            print_round_header("Managerial & Leadership", job.title, candidate_name, duration_minutes, extra_info={"👔 Leadership Dimensions": str(len(blueprint.targets))})
            
            question_generator = ManagerialQuestionGenerator(self.llm)
            
            while session.state not in (InterviewState.CLOSING, InterviewState.COMPLETED):
                if session.state == InterviewState.QUESTIONING:
                    target_competency = blueprint.targets[0].competency
                    for target in blueprint.targets:
                        if target.competency not in session.covered_competencies:
                            target_competency = target.competency
                            break
                            
                    transcript_text = "\n".join(f"{msg.role}: {msg.content}" for msg in session.transcript)
                    with show_thinking_spinner(f"Generating leadership scenario for {target_competency}..."):
                        question = await question_generator.generate(job, target_competency, transcript_text)
                    engine.ask(session, question)
                
                print_question_card(session.questions_asked + 1, 5, session.current_question, competency=target_competency)
                answer = prompt_candidate_answer()
                
                if not answer or answer.lower() in ('quit', 'exit', 'done', 'finish', 'stop'):
                    print("\n[Candidate requested to conclude interview.]")
                    break
                
                context = InterviewContextBuilder().build(job=job, session=session)
                with show_thinking_spinner("Evaluating managerial tradeoffs & situational leadership..."):
                    decision = await engine.process_answer(context, answer)
                
                if session.scores:
                    latest = session.scores[-1]
                    print_evaluation_card(
                        score=latest.score,
                        strengths=latest.strengths,
                        weaknesses=latest.weaknesses,
                        feedback=f"Assessed on {target_competency}."
                    )
                
                if session.questions_asked >= 5 or session.is_time_up:
                    engine.state_machine.transition(session, InterviewEvent.END)
                    break
                    
            engine.close(session)
            overall_score = sum(s.score for s in session.scores) / len(session.scores) if session.scores else 0.85
            print_final_scorecard("Managerial & Leadership", candidate_name, overall_score, assessments=session.scores)
            return overall_score

        elif interview_type == "project":
            from interviewos.interview.strategies.project import ProjectInterviewStrategy
            from interviewos.interview.project import GitHubClient, ProjectAnalysisAgent
            from interviewos.config import get_settings
            
            strategy = ProjectInterviewStrategy()
            settings = get_settings()
            
            if not github_url:
                github_url = input("\nEnter GitHub repository URL for project deep dive: ").strip()
                
            if not github_url:
                print("No repository provided. Ending project interview.")
                return 0.0
                
            with show_thinking_spinner(f"Analyzing GitHub repository {github_url}..."):
                github_client = GitHubClient(token=settings.github_token)
                agent = ProjectAnalysisAgent(self.llm, github_client)
                project_profile = await agent.analyze(github_url)
            
            session = InterviewSession(
                id=str(uuid.uuid4()),
                interview_type=InterviewType.PROJECT,
                candidate_id=candidate_name,
                job_id="job",
                duration_minutes=duration_minutes,
                project_profile=project_profile,
            )
            
            engine = InterviewEngine(
                interviewer=Interviewer(self.llm),
                state_machine=InterviewStateMachine(),
                brain=InterviewBrain(self.llm, Interviewer(self.llm), strategy)
            )
            
            engine.start(session)
            print_round_header("Project Deep Dive", job.title, candidate_name, duration_minutes, extra_info={"🔗 Repository": project_profile.repository_name, "📁 Discovered Files": str(len(project_profile.dependencies.files))})
            
            first_question = f"Could you give an architectural overview of your {project_profile.repository_name} project, and explain the major design decisions you made?"
            engine.ask(session, first_question)
            
            while session.state not in (InterviewState.CLOSING, InterviewState.COMPLETED):
                print_question_card(session.questions_asked + 1, 5, session.current_question, competency="System Architecture & Code Ownership")
                answer = prompt_candidate_answer()
                
                if not answer or answer.lower() in ('quit', 'exit', 'done', 'finish', 'stop'):
                    print("\n[Candidate requested to conclude interview.]")
                    break
                
                context = InterviewContextBuilder().build(job=job, session=session, project_profile=project_profile)
                context = InterviewContextBuilder().with_project(context, project_profile)
                with show_thinking_spinner("Probing codebase architecture & implementation tradeoffs..."):
                    decision = await engine.process_answer(context, answer)
                
                if session.scores:
                    latest = session.scores[-1]
                    print_evaluation_card(
                        score=latest.score,
                        strengths=latest.strengths,
                        weaknesses=latest.weaknesses,
                        feedback="Assessed on architectural ownership."
                    )
                
                if session.questions_asked >= 5 or session.is_time_up:
                    engine.state_machine.transition(session, InterviewEvent.END)
                    break
                    
            engine.close(session)
            overall_score = sum(s.score for s in session.scores) / len(session.scores) if session.scores else 0.85
            print_final_scorecard("Project Deep Dive", candidate_name, overall_score, assessments=session.scores)
            return overall_score

        else:
            print(f"Terminal flow for {interview_type} is not yet fully implemented.")
            return 0.0

    async def run_hiring(
        self,
        candidate_name: str,
        candidate_email: str,
        plan_path: Path | None = None,
    ) -> None:
        """Run the multi-round hiring process."""
        await self.analyze_documents_async()
        
        from interviewos.orchestrator.plan import InterviewPlanGenerator
        from interviewos.orchestrator.engine import InterviewOrchestrator
        from interviewos.orchestrator.models import CandidateStatus
        from interviewos.orchestrator.models import InterviewPlan

        job = self.job
        
        print("\n========================================")
        print("INTERVIEWOS INTERVIEW PROCESS")
        print(f"Role: {job.title}")
        print("========================================\n")
        
        if plan_path and plan_path.exists():
            print("Loading Interview Plan...")
            plan_json = plan_path.read_text()
            plan = InterviewPlan.model_validate_json(plan_json)
        else:
            print("Generating Interview Plan based on JD...")
            generator = InterviewPlanGenerator(self.llm)
            plan = await generator.generate(job)
            
        print(f"Interview Plan loaded with {len(plan.rounds)} rounds.")
        for r in plan.rounds:
            print(f"- {r.name} ({r.type}) Threshold: {r.threshold}")
            
        orchestrator = InterviewOrchestrator(self.llm)
        
        async def run_interactive_round(round_config, context, job_profile):
            from interviewos.orchestrator.models import RoundResult, RoundStatus, InterviewRoundType
            from datetime import datetime
            
            if round_config.type == InterviewRoundType.OA:
                score = await self.run_oa(
                    candidate_name=candidate_name,
                    candidate_email=candidate_email,
                    total_questions=10,
                    duration_minutes=round_config.duration_minutes,
                    threshold=round_config.threshold or 0.7,
                    job=job_profile
                )
            else:
                score = await self.run_interview(
                    interview_type=round_config.type.value,
                    candidate_name=candidate_name,
                    candidate_email=candidate_email,
                    duration_minutes=round_config.duration_minutes,
                    difficulty="Medium",
                    job=job_profile
                )
                
            return RoundResult(
                round_id=round_config.round_id,
                round_type=round_config.type,
                score=score or 0.0,
                status=RoundStatus.COMPLETED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_minutes=round_config.duration_minutes
            )
        
        evaluation = await orchestrator.run_process(
            plan=plan,
            candidate_id=candidate_name,
            job=job,
            resume=self.resume,
            round_executor=run_interactive_round
        )
        
        print("\n========================================")
        if evaluation.final_status == CandidateStatus.SHORTLISTED:
            print("CANDIDATE SHORTLISTED")
        else:
            print("CANDIDATE NOT SHORTLISTED")
            
        if evaluation.weighted_score is not None:
            print(f"Overall Score: {evaluation.weighted_score*100:.1f}%")
        print(f"Rounds Completed: {evaluation.rounds_completed}")
        print("========================================\n")

    def run_ranking(
        self,
        results_dir: Path,
    ) -> None:
        """Rank candidates based on final evaluations."""
        import json
        from interviewos.orchestrator.models import FinalInterviewEvaluation
        from interviewos.orchestrator.ranking import RankingEngine
        
        print("\n========================================")
        print("CANDIDATE RANKING")
        print("=================")
        
        if not results_dir.exists():
            print(f"Error: Results directory '{results_dir}' not found.")
            return
            
        evaluations = []
        for file in results_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text())
                eval_obj = FinalInterviewEvaluation(**data)
                evaluations.append(eval_obj)
            except Exception as e:
                print(f"Skipping {file.name}: invalid format ({e})")
                
        if not evaluations:
            print("No valid evaluation files found.")
            return
            
        engine = RankingEngine(policy="threshold_only")
        ranked_candidates = engine.rank(evaluations)
        
        print("\nRank  Candidate       Score   Status")
        print("-" * 50)
        
        for i, candidate in enumerate(ranked_candidates, start=1):
            score_str = f"{candidate.weighted_score*100:.0f}%" if candidate.weighted_score is not None else "N/A"
            status_str = candidate.final_status.value.replace("_", " ").upper()
            
            # Format nicely
            rank_col = str(i).ljust(5)
            cand_col = candidate.candidate_id.ljust(15)
            score_col = score_str.ljust(7)
            
            print(f"{rank_col} {cand_col} {score_col} {status_str}")
        print("========================================\n")