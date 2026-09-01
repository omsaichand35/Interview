from interviewos.models import (
    LearnerState,
    LearningProgress,
)
from interviewos.models.plan import PreparationPlan
from interviewos.models import EvaluationResult


class LearnerStateManager:
    """Manage the candidate's evolving learning state."""

    def __init__(
        self,
        state: LearnerState | None = None,
    ) -> None:
        self.state = state or LearnerState()

    def set_candidate(
        self,
        candidate_name: str | None,
        target_role: str | None,
    ) -> None:
        """Set candidate and target-role information."""

        self.state.candidate_name = candidate_name
        self.state.target_role = target_role

    def initialize_from_plan(
        self,
        plan: PreparationPlan,
    ) -> None:
        """Initialize learning progress from a preparation plan."""

        self.state.target_role = plan.goal

        # Keep a map of existing progress
        existing_progress = {
            progress.topic.lower(): progress
            for progress in self.state.progress
        }

        all_nodes = plan.get_all_nodes()
        for node in all_nodes.values():
            topic_lower = node.title.lower()
            notes = []
            for record in node.assessment_history:
                if record.notes:
                    notes.append(record.notes)
                    
            if topic_lower in existing_progress:
                prog = existing_progress[topic_lower]
                prog.mastery_score = node.mastery_score / 100.0
                prog.completed = (node.mastery_score >= 80.0)
                prog.priority = node.priority.value
                # Append new notes if any
                for n in notes:
                    if n not in prog.notes:
                        prog.notes.append(n)
                continue

            self.state.progress.append(
                LearningProgress(
                    topic=node.title,
                    mastery_score=node.mastery_score / 100.0, # convert 0-100 to 0-1
                    completed=(node.mastery_score >= 80.0),
                    notes=notes,
                    priority=node.priority.value
                )
            )

    def update_mastery(
        self,
        topic: str,
        mastery_score: float,
        note: str | None = None,
    ) -> None:
        """Update mastery for a topic."""

        mastery_score = max(
            0.0,
            min(1.0, mastery_score),
        )

        for progress in self.state.progress:
            if progress.topic.lower() == topic.lower():
                progress.mastery_score = mastery_score
                progress.completed = mastery_score >= 0.8

                if note:
                    progress.notes.append(note)

                return

        self.state.progress.append(
            LearningProgress(
                topic=topic,
                mastery_score=mastery_score,
                completed=mastery_score >= 0.8,
                notes=[note] if note else [],
            )
        )

    def get_weak_topics(
        self,
        threshold: float = 0.5,
    ) -> list[str]:
        """Return topics whose mastery is below the threshold."""

        return [
            progress.topic
            for progress in self.state.progress
            if progress.mastery_score < threshold
        ]

    def get_state(self) -> LearnerState:
        """Return the current learner state."""

        return self.state

    def apply_evaluation(
            self,
            evaluation: EvaluationResult,
    ) -> None:
        """Update learner state from an evaluation."""

        self.update_mastery(
            topic=evaluation.topic,
            mastery_score=evaluation.score,
            note=evaluation.feedback,
        )