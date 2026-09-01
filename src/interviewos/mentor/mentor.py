from interviewos.llm import LLMClient
from interviewos.models import (
    EvaluationResult,
    LearnerState,
    PracticeQuestion,
)
from interviewos.models.plan import PreparationPlan

from interviewos.rag import RAGPipeline

from .conversation import ConversationManager
from .learner_state import LearnerStateManager
from .tutor import Tutor
from .evaluator import MentorEvaluator
from .practice import PracticeGenerator
from .agent import MentorAgent

from interviewos.models import (
    EvaluationResult,
    LearningPlan,
    LearnerState,
    MentorAction,
    MentorDecision,
)


class Mentor:
    """Main AI mentor for interview preparation."""

    def __init__(
        self,
        llm: LLMClient,
        rag: RAGPipeline,
        state: LearnerState | None = None,
        learning_plan: PreparationPlan | None = None,
    ) -> None:

        self.llm = llm
        self.rag = rag

        self.state_manager = LearnerStateManager(
            state
        )

        self.state = self.state_manager.get_state()

        self.conversation_manager = (
            ConversationManager(self.state)
        )

        self.tutor = Tutor(llm)

        self.learning_plan = learning_plan

        if learning_plan:
            self.state_manager.initialize_from_plan(
                learning_plan
            )

        self.evaluator = MentorEvaluator(llm)

        self.practice_generator = PracticeGenerator(
            llm
        )
        self.agent = MentorAgent(llm)

    def set_learning_plan(
        self,
        learning_plan: PreparationPlan,
    ) -> None:
        """Attach a learning plan to the mentor."""

        self.learning_plan = learning_plan

        self.state_manager.initialize_from_plan(
            learning_plan
        )

    def ask(
        self,
        message: str,
    ) -> str:
        """Process one candidate message."""

        if not message.strip():
            raise ValueError(
                "Mentor message cannot be empty."
            )

        self.conversation_manager.add_user_message(
            message
        )

        retrieval_results = self.rag.retrieve(
            query=message,
            limit=5,
        )

        context_parts = [
            result.chunk.content
            for result in retrieval_results
        ]

        context = "\n\n---\n\n".join(
            context_parts
        )

        history = (
            self.conversation_manager.format_history(
                limit=10
            )
        )

        response = self.tutor.respond(
            message=message,
            state=self.state,
            learning_plan=self.learning_plan,
            context=context,
            conversation=history,
        )

        self.conversation_manager.add_mentor_message(
            response
        )

        return response

    def get_state(self) -> LearnerState:
        """Return current learner state."""

        return self.state_manager.get_state()

    def practice(
            self,
            topic: str,
            difficulty: str = "medium",
    ):
        """Generate a practice question."""

        retrieval_results = self.rag.retrieve(
            query=topic,
            limit=5,
        )

        context = "\n\n---\n\n".join(
            result.chunk.content
            for result in retrieval_results
        )

        question = self.practice_generator.generate(
            topic=topic,
            state=self.state,
            context=context,
            difficulty=difficulty,
        )

        return question

    def evaluate_answer(
            self,
            topic: str,
            question: str,
            answer: str,
    ) -> EvaluationResult:
        """Evaluate a candidate answer and update learner state."""

        retrieval_results = self.rag.retrieve(
            query=question,
            limit=5,
        )

        context = "\n\n---\n\n".join(
            result.chunk.content
            for result in retrieval_results
        )

        evaluation = self.evaluator.evaluate(
            topic=topic,
            question=question,
            candidate_answer=answer,
            reference_context=context,
            state=self.state,
        )

        self.state_manager.apply_evaluation(
            evaluation
        )

        return evaluation

    def interact(
            self,
            message: str,
    ) -> str:
        """Process a candidate interaction."""

        if not message.strip():
            raise ValueError(
                "Mentor message cannot be empty."
            )

        self.conversation_manager.add_user_message(
            message
        )

        decision = self.agent.decide(
            message=message,
            state=self.state,
            learning_plan=self.learning_plan,
        )

        if decision.action == MentorAction.TEACH:
            response = self._generate_teaching_response(
                message,
                decision,
            )

        elif decision.action == MentorAction.PRACTICE:
            response = self._generate_practice_response(
                decision,
            )

        elif decision.action == MentorAction.REVIEW:
            response = self._generate_review_response(
                decision,
            )

        elif decision.action == MentorAction.MOVE_FORWARD:
            response = self._generate_move_forward_response(
                decision,
            )

        else:
            response = self._generate_clarification_response(
                message
            )

        self.conversation_manager.add_mentor_message(
            response
        )

        return response

    def _generate_teaching_response(
            self,
            message: str,
            decision: MentorDecision,
    ) -> str:

        topic = decision.topic or message

        results = self.rag.retrieve(
            query=decision.retrieval_query or topic,
            limit=5,
        )

        context = "\n\n---\n\n".join(
            result.chunk.content
            for result in results
        )

        history = self.conversation_manager.format_history(
            limit=10
        )

        return self.tutor.respond(
            message=message,
            state=self.state,
            learning_plan=self.learning_plan,
            context=context,
            conversation=history,
        )

    def _generate_practice_response(
            self,
            decision: MentorDecision,
    ) -> str:

        topic = decision.topic

        if not topic:
            weak_topics = (
                self.state_manager.get_weak_topics()
            )

            topic = (
                weak_topics[0]
                if weak_topics
                else "interview fundamentals"
            )

        self.state.current_topic = topic

        question = self.practice_generator.generate(
            topic=topic,
            state=self.state,
            difficulty=decision.difficulty,
        )

        return question.question

    def _generate_review_response(
            self,
            decision: MentorDecision,
    ) -> str:

        topic = decision.topic

        if not topic:
            weak_topics = (
                self.state_manager.get_weak_topics()
            )

            if not weak_topics:
                return (
                    "Your current topics look reasonably strong. "
                    "Let's move forward."
                )

            topic = weak_topics[0]

        self.state.current_topic = topic

        return self._generate_teaching_response(
            f"Review {topic}.",
            MentorDecision(
                action=MentorAction.TEACH,
                topic=topic,
                reasoning="Weak topic review.",
                retrieval_query=topic,
            ),
        )

    def _generate_move_forward_response(
            self,
            decision: MentorDecision,
    ) -> str:

        if decision.topic:
            self.state.current_topic = decision.topic

            return self._generate_teaching_response(
                f"Start teaching {decision.topic}.",
                decision,
            )

        return (
            "You've demonstrated enough understanding here. "
            "Let's move to the next topic."
        )

    def _generate_clarification_response(
            self,
            message: str,
    ) -> str:

        return self.tutor.respond(
            message=message,
            state=self.state,
            learning_plan=self.learning_plan,
            context="",
            conversation=self.conversation_manager.format_history(
                limit=10
            ),
        )

    def _execute_practice(
            self,
            decision: MentorDecision,
    ) -> str:
        """Execute a practice-question action."""

        topic = decision.topic

        if not topic:
            weak_topics = (
                self.state_manager.get_weak_topics()
            )

            if weak_topics:
                topic = weak_topics[0]
            else:
                topic = (
                        self.state.current_topic
                        or "interview fundamentals"
                )

        question = self.practice_generator.generate(
            topic=topic,
            state=self.state,
            difficulty=decision.difficulty,
        )

        self.state.current_topic = topic

        return question.model_dump_json(
            indent=2
        )

    def _execute_move_forward(
            self,
            decision: MentorDecision,
    ) -> str:
        """Move to the next learning topic."""

        topic = decision.topic

        if topic:
            self.state.current_topic = topic

            return self._execute_teach(
                f"Teach me {topic}.",
                MentorDecision(
                    action=MentorAction.TEACH,
                    topic=topic,
                    reasoning="Moving to the next topic.",
                    retrieval_query=topic,
                    difficulty="medium",
                ),
            )

        return (
            "You are ready to move forward. "
            "Let's continue with the next topic in your plan."
        )

    def _execute_clarify(
            self,
            message: str,
            decision: MentorDecision,
    ) -> str:
        """Ask the candidate for clarification."""

        response = self.tutor.respond(
            message=message,
            state=self.state,
            learning_plan=self.learning_plan,
            context="",
            conversation=self.conversation_manager.format_history(
                limit=10
            ),
        )

        self.conversation_manager.add_user_message(
            message
        )

        self.conversation_manager.add_mentor_message(
            response
        )

        return response