from datetime import datetime
import uuid

from interviewos.models import JobProfile
from interviewos.interview.engine import InterviewEngine
from interviewos.interview.session import InterviewSession, InterviewType
from interviewos.interview.state_machine import InterviewStateMachine
from interviewos.interview.brain import InterviewBrain
from interviewos.interview.interviewer import Interviewer
from interviewos.assessment.oa import AssessmentSession, OAEngine, AssessmentBlueprint, AssessmentSessionStatus

from .models import (
    InterviewPlan, 
    CandidateInterviewContext, 
    RoundResult, 
    InterviewRoundType, 
    RoundStatus, 
    CandidateStatus,
    ShortlistPolicy,
    FinalInterviewEvaluation
)

class InterviewOrchestrator:
    """Coordinates multiple independent interview rounds."""
    
    def __init__(self, llm):
        self.llm = llm
        
    async def run_process(
        self, 
        plan: InterviewPlan, 
        candidate_id: str, 
        job: JobProfile, 
        resume=None,
        round_executor=None
    ) -> FinalInterviewEvaluation:
        """Executes the interview plan sequentially."""
        
        context = CandidateInterviewContext(
            candidate_id=candidate_id,
            job_id="job",
            resume_id="resume" if resume else None,
            interview_plan_id=plan.plan_id
        )
        
        rounds = sorted(plan.rounds, key=lambda r: r.order)
        candidate_status = CandidateStatus.IN_PROGRESS
        
        for round_config in rounds:
            if not round_config.enabled:
                context.round_results[round_config.round_id] = RoundResult(
                    round_id=round_config.round_id,
                    round_type=round_config.type,
                    score=0.0,
                    status=RoundStatus.SKIPPED
                )
                continue
                
            context.current_round_type = round_config.type
            print(f"\n========================================")
            print(f"Starting Round: {round_config.name} ({round_config.type})")
            print(f"========================================")
            
            # Execute round
            try:
                if round_executor:
                    result = await round_executor(round_config, context, job)
                else:
                    result = await self.execute_round(round_config, context, job)

            except Exception as e:
                # In production, use standard logging instead of print
                print(f"[Orchestrator] Critical error executing round {round_config.name}: {e}")
                from interviewos.core.exceptions import LLMError
                
                result = RoundResult(
                    round_id=round_config.round_id,
                    round_type=round_config.type,
                    score=0.0,
                    status=RoundStatus.FAILED,
                )
            
            context.round_results[round_config.round_id] = result
            context.completed_rounds.append(round_config.round_id)
            
            # Check Threshold
            if round_config.threshold is not None:
                if result.score >= round_config.threshold:
                    result.status = RoundStatus.PASSED
                    print(f"ROUND RESULT: Score: {result.score*100:.1f}%, Status: PASSED (Threshold: {round_config.threshold*100:.1f}%)")
                else:
                    result.status = RoundStatus.FAILED
                    print(f"ROUND RESULT: Score: {result.score*100:.1f}%, Status: FAILED (Threshold: {round_config.threshold*100:.1f}%)")
                    
                    stop_on_failure = plan.configuration.get("stop_on_failure", True)
                    if round_config.required and stop_on_failure:
                        print(f"\n[System: Candidate did not meet the required {round_config.name} threshold. Ending process.]")
                        candidate_status = CandidateStatus.NOT_SHORTLISTED
                        break
            else:
                result.status = RoundStatus.COMPLETED
                print(f"ROUND RESULT: Score: {result.score*100:.1f}%, Status: COMPLETED")
                
            self._update_cross_round_context(context, result)
            
        if candidate_status == CandidateStatus.IN_PROGRESS:
            candidate_status = CandidateStatus.COMPLETED
            
        return self.build_final_evaluation(plan, context, candidate_status, job)
        
    async def execute_round(self, round_config, context: CandidateInterviewContext, job: JobProfile) -> RoundResult:
        if round_config.type == InterviewRoundType.OA:
            return await self.execute_oa(round_config, job)
        else:
            return await self.execute_interview(round_config, context, job)
            
    async def execute_oa(self, round_config, job: JobProfile) -> RoundResult:
        # Mocking OA execution structure
        # In a real setup, we would call the actual OA terminal runner, but we shouldn't block the terminal loop here.
        # For orchestrator purposes we will assume the OA completes and returns a score.
        # Since we cannot inject `input()` cleanly for the whole loop here if we just want the engine, 
        # we will use the engine to evaluate.
        # To avoid duplicating the CLI loop, we'll return a simulated or actual result.
        
        print("Executing OA (Orchestrator boundary)...")
        # For integration testing, we just return a fake result or let the mock handle it.
        # Here we just construct a RoundResult for the OA.
        # In a real environment, we'd trigger `TerminalOARunner` or similar.
        
        # We will simulate the OA result for now as the orchestrator handles flow.
        return RoundResult(
            round_id=round_config.round_id,
            round_type=round_config.type,
            score=0.75, # Simulated
            status=RoundStatus.COMPLETED,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_minutes=round_config.duration_minutes
        )
        
    async def execute_interview(self, round_config, context: CandidateInterviewContext, job: JobProfile) -> RoundResult:
        strategy = self._get_strategy(round_config.type)
        
        session = InterviewSession(
            id=str(uuid.uuid4()),
            interview_type=InterviewType(round_config.type.value),
            candidate_id=context.candidate_id,
            job_id=context.job_id,
            duration_minutes=round_config.duration_minutes
        )
        
        engine = InterviewEngine(
            interviewer=Interviewer(self.llm),
            state_machine=InterviewStateMachine(),
            brain=InterviewBrain(self.llm, Interviewer(self.llm), strategy)
        )
        
        # We simulate the interview loop completing and aggregating scores.
        # In real code, this would invoke a terminal loop or UI driver.
        # We return a RoundResult placeholder for testing.
        return RoundResult(
            round_id=round_config.round_id,
            round_type=round_config.type,
            score=0.80, # Simulated
            status=RoundStatus.COMPLETED,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_minutes=round_config.duration_minutes
        )
        
    def _get_strategy(self, round_type: InterviewRoundType):
        if round_type == InterviewRoundType.TECHNICAL:
            from interviewos.interview.strategies.technical import TechnicalInterviewStrategy
            return TechnicalInterviewStrategy()
        elif round_type == InterviewRoundType.DSA:
            from interviewos.interview.strategies.dsa import DSAInterviewStrategy
            return DSAInterviewStrategy()
        elif round_type == InterviewRoundType.HR:
            from interviewos.interview.strategies.hr import HRInterviewStrategy
            return HRInterviewStrategy()
        elif round_type == InterviewRoundType.MANAGERIAL:
            from interviewos.interview.strategies.managerial import ManagerialInterviewStrategy
            return ManagerialInterviewStrategy()
        elif round_type == InterviewRoundType.PROJECT:
            # Project round uses GitHub agent — in orchestrator context we return a
            # placeholder strategy. Full project interview is driven from the CLI directly.
            from interviewos.interview.strategies.technical import TechnicalInterviewStrategy
            return TechnicalInterviewStrategy()
        else:
            raise ValueError(f"Unsupported strategy for round type: {round_type}")

    def _update_cross_round_context(self, context: CandidateInterviewContext, result: RoundResult):
        context.weaknesses.extend(result.weaknesses)
        context.strengths.extend(result.strengths)
        context.topics_already_tested.extend(result.competencies.keys())
        
    def build_final_evaluation(
        self, 
        plan: InterviewPlan, 
        context: CandidateInterviewContext, 
        candidate_status: CandidateStatus,
        job: JobProfile
    ) -> FinalInterviewEvaluation:
        from interviewos.orchestrator.models import FinalCandidateStatus
        
        scores = {}
        weighted_score = 0.0
        total_weight = 0.0
        
        all_required_passed = True
        
        all_strengths = []
        all_weaknesses = []
        
        for r in plan.rounds:
            if not r.enabled:
                continue
            res = context.round_results.get(r.round_id)
            if res and res.status != RoundStatus.SKIPPED:
                scores[r.type.value] = res.score
                weight = r.configuration.get("weight", 1.0)
                weighted_score += res.score * weight
                total_weight += weight
                
                all_strengths.extend(res.strengths)
                all_weaknesses.extend(res.weaknesses)
                
                if r.required and res.status == RoundStatus.FAILED:
                    all_required_passed = False
                    
        if total_weight > 0:
            weighted_score /= total_weight
            
        policy = plan.configuration.get("shortlist_policy", ShortlistPolicy.HYBRID)
        
        final_status = FinalCandidateStatus.INCOMPLETE
        
        if candidate_status in (CandidateStatus.COMPLETED, CandidateStatus.NOT_SHORTLISTED, CandidateStatus.SHORTLISTED):
            if policy == ShortlistPolicy.HYBRID:
                if all_required_passed and (plan.final_threshold is None or weighted_score >= plan.final_threshold):
                    final_status = FinalCandidateStatus.SHORTLISTED
                else:
                    final_status = FinalCandidateStatus.NOT_SHORTLISTED
            elif policy == ShortlistPolicy.ALL_REQUIRED_ROUNDS_PASS:
                if all_required_passed:
                    final_status = FinalCandidateStatus.SHORTLISTED
                else:
                    final_status = FinalCandidateStatus.NOT_SHORTLISTED
            elif policy == ShortlistPolicy.WEIGHTED_SCORE:
                if plan.final_threshold is None or weighted_score >= plan.final_threshold:
                    final_status = FinalCandidateStatus.SHORTLISTED
                else:
                    final_status = FinalCandidateStatus.NOT_SHORTLISTED
        elif candidate_status == CandidateStatus.FAILED:
             final_status = FinalCandidateStatus.NOT_SHORTLISTED
             
        # JD Coverage
        jd_coverage = {}
        tested_lower = [t.lower() for t in context.topics_already_tested]
        
        # We'll use a simple deterministic match
        all_skills = job.required_skills + job.preferred_skills
        for skill in all_skills:
            skill_name_lower = skill.name.lower()
            if skill_name_lower in tested_lower:
                jd_coverage[skill.name] = "TESTED"
            else:
                # Basic partial check - if any word matches
                words = skill_name_lower.split()
                if any(w in tested_lower or any(w in t for t in tested_lower) for w in words):
                    jd_coverage[skill.name] = "PARTIAL"
                else:
                    jd_coverage[skill.name] = "NOT_TESTED"
                    
        # Deduplicate
        unique_strengths = list(dict.fromkeys(all_strengths))
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))
                    
        return FinalInterviewEvaluation(
            candidate_id=context.candidate_id,
            role=plan.role,
            rounds_completed=len(scores),
            round_scores=scores,
            weighted_score=weighted_score if total_weight > 0 else None,
            final_status=final_status,
            jd_coverage=jd_coverage,
            strengths=unique_strengths,
            weaknesses=unique_weaknesses,
            recommendation="Proceed" if final_status == FinalCandidateStatus.SHORTLISTED else "Reject"
        )
