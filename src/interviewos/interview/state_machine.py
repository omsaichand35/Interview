from .session import InterviewSession
from .state import InterviewEvent, InterviewState


class InterviewStateMachine:
    """Control valid interview state transitions."""

    _TRANSITIONS = {
        InterviewState.CREATED: {
            InterviewEvent.START:
                InterviewState.INTRODUCTION,
        },

        InterviewState.INTRODUCTION: {
            InterviewEvent.INTRODUCTION_COMPLETE:
                InterviewState.QUESTIONING,
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.QUESTIONING,
            InterviewEvent.PRESENT_PROBLEM:
                InterviewState.PROBLEM_PRESENTATION,
            InterviewEvent.END:
                InterviewState.COMPLETED,
        },


        InterviewState.PROBLEM_PRESENTATION: {
            InterviewEvent.MOVE_TO_UNDERSTANDING:
                InterviewState.UNDERSTANDING,
            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.UNDERSTANDING: {
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.UNDERSTANDING,
            InterviewEvent.FOLLOW_UP_REQUIRED:
                InterviewState.UNDERSTANDING,
            InterviewEvent.DEEP_DIVE_REQUIRED:
                InterviewState.UNDERSTANDING,
            InterviewEvent.MOVE_TO_APPROACH:
                InterviewState.APPROACH,
            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.APPROACH: {
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.APPROACH,
            InterviewEvent.FOLLOW_UP_REQUIRED:
                InterviewState.APPROACH,
            InterviewEvent.DEEP_DIVE_REQUIRED:
                InterviewState.APPROACH,
            InterviewEvent.MOVE_TO_OPTIMIZATION:
                InterviewState.OPTIMIZATION,
            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.OPTIMIZATION: {
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.OPTIMIZATION,
            InterviewEvent.FOLLOW_UP_REQUIRED:
                InterviewState.OPTIMIZATION,
            InterviewEvent.DEEP_DIVE_REQUIRED:
                InterviewState.OPTIMIZATION,
            InterviewEvent.NEXT_PROBLEM:
                InterviewState.PROBLEM_PRESENTATION,
            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.QUESTIONING: {
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.QUESTIONING,

            InterviewEvent.FOLLOW_UP_REQUIRED:
                InterviewState.FOLLOW_UP,

            InterviewEvent.DEEP_DIVE_REQUIRED:
                InterviewState.DEEP_DIVE,

            InterviewEvent.PRESENT_PROBLEM:
                InterviewState.PROBLEM_PRESENTATION,

            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.FOLLOW_UP: {
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.QUESTIONING,

            InterviewEvent.DEEP_DIVE_REQUIRED:
                InterviewState.DEEP_DIVE,

            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.DEEP_DIVE: {
            InterviewEvent.ANSWER_RECEIVED:
                InterviewState.QUESTIONING,

            InterviewEvent.END:
                InterviewState.CLOSING,
        },

        InterviewState.CLOSING: {
            InterviewEvent.END:
                InterviewState.COMPLETED,
        },

        InterviewState.COMPLETED: {},
    }

    def transition(
        self,
        session: InterviewSession,
        event: InterviewEvent,
    ) -> InterviewState:
        """Transition the session to a new state."""

        current = session.state

        transitions = self._TRANSITIONS.get(
            current,
            {},
        )

        new_state = transitions.get(
            event
        )

        if new_state is None:
            raise ValueError(
                f"Invalid interview transition: "
                f"{current.value} -> "
                f"{event.value}"
            )

        session.state = new_state

        return new_state