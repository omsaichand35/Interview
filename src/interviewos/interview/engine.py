from datetime import datetime

from .interviewer import Interviewer
from .session import InterviewSession, InterviewScore
from .state import InterviewEvent, InterviewState
from .state_machine import InterviewStateMachine

from interviewos.models import JobProfile

from .context import InterviewContext

from .brain import InterviewBrain
from .session import (
    InterviewDecision,
    InterviewSession,
)
from .state import (
    InterviewAction,
    InterviewEvent,
)

class InterviewEngine:
    """Core engine for adaptive interviews."""

    def __init__(
            self,
            interviewer: Interviewer,
            state_machine: InterviewStateMachine,
            brain: InterviewBrain,
    ) -> None:

        self.interviewer = interviewer
        self.state_machine = state_machine
        self.brain = brain

    def start(
        self,
        session: InterviewSession,
    ) -> InterviewSession:
        """Start an interview."""

        self.state_machine.transition(
            session,
            InterviewEvent.START,
        )

        session.started_at = datetime.now()

        return session

    def introduce(
        self,
        session: InterviewSession,
        introduction: str,
    ) -> None:
        """Complete the introduction."""

        session.add_message(
            role="interviewer",
            content=introduction,
        )

        self.state_machine.transition(
            session,
            InterviewEvent.INTRODUCTION_COMPLETE,
        )

    def ask(
        self,
        session: InterviewSession,
        question: str,
        evidence: list['InterviewQuestionEvidence'] | None = None,
    ) -> None:
        """Ask a question."""

        session.current_question = question
        session.current_question_evidence = evidence or []

        session.questions_asked += 1

        session.add_message(
            role="interviewer",
            content=question,
        )

    def receive_answer(
        self,
        session: InterviewSession,
        answer: str,
    ) -> None:
        """Receive a candidate answer."""

        session.add_message(
            role="candidate",
            content=answer,
        )

        self.state_machine.transition(
            session,
            InterviewEvent.ANSWER_RECEIVED,
        )

    def request_follow_up(
        self,
        session: InterviewSession,
    ) -> None:
        """Move into follow-up questioning."""

        self.state_machine.transition(
            session,
            InterviewEvent.FOLLOW_UP_REQUIRED,
        )

    def request_deep_dive(
        self,
        session: InterviewSession,
    ) -> None:
        """Move into deep-dive questioning."""

        self.state_machine.transition(
            session,
            InterviewEvent.DEEP_DIVE_REQUIRED,
        )

    def close(
        self,
        session: InterviewSession,
    ) -> None:
        """Close the interview."""
        if session.state == InterviewState.COMPLETED:
            return

        if session.state != InterviewState.CLOSING:
            self.state_machine.transition(
                session,
                InterviewEvent.END,
            )

        if session.state == InterviewState.CLOSING:
            self.state_machine.transition(
                session,
                InterviewEvent.END,
            )

        if session.completed_at is None:
            session.completed_at = datetime.now()

    def _apply_decision(
            self,
            session: InterviewSession,
            decision: InterviewDecision,
    ) -> None:
        """Apply an interviewer decision to the session."""

        session.scores.append(
            InterviewScore(
                competency=(
                        decision.next_competency
                        or "general"
                ),
                score=decision.assessment.score,
                feedback=decision.assessment.feedback,
            )
        )

        if (
                decision.action
                == InterviewAction.ASK_FOLLOW_UP
        ):
            self.state_machine.transition(
                session,
                InterviewEvent.FOLLOW_UP_REQUIRED,
            )

            if decision.next_question:
                self.ask(
                    session,
                    decision.next_question,
                    decision.question_evidence,
                )

            return

        if (
                decision.action
                == InterviewAction.DEEP_DIVE
        ):
            self.state_machine.transition(
                session,
                InterviewEvent.DEEP_DIVE_REQUIRED,
            )

            if decision.next_question:
                self.ask(
                    session,
                    decision.next_question,
                    decision.question_evidence,
                )

            return

        if (
                decision.action
                == InterviewAction.MOVE_ON
        ):
            if session.state == InterviewState.PROBLEM_PRESENTATION:
                self.state_machine.transition(session, InterviewEvent.MOVE_TO_UNDERSTANDING)
            elif session.state == InterviewState.UNDERSTANDING:
                self.state_machine.transition(session, InterviewEvent.MOVE_TO_APPROACH)
            elif session.state == InterviewState.APPROACH:
                self.state_machine.transition(session, InterviewEvent.MOVE_TO_OPTIMIZATION)
            elif session.state == InterviewState.OPTIMIZATION:
                self.state_machine.transition(session, InterviewEvent.NEXT_PROBLEM)
            else:
                session.state = InterviewState.QUESTIONING

            if decision.next_question:
                self.ask(
                    session,
                    decision.next_question,
                    decision.question_evidence,
                )

            return

        if (
                decision.action
                == InterviewAction.END_INTERVIEW
        ):
            if decision.next_question:
                self.ask(
                    session,
                    decision.next_question,
                    decision.question_evidence,
                )
            self.close(
                session
            )

    async def process_answer(
            self,
            context: InterviewContext,
            answer: str,
    ) -> InterviewDecision:
        """Process and evaluate a candidate answer."""

        session = context.session

        self.receive_answer(
            session,
            answer,
        )

        decision = await self.brain.evaluate_answer(
            context
        )

        self._apply_decision(
            session,
            decision,
        )

        return decision
