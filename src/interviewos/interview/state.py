from enum import StrEnum


class InterviewType(StrEnum):
    """Supported interview types."""

    TECHNICAL = "technical"
    DSA = "dsa"
    PROJECT = "project"
    HR = "hr"
    MANAGERIAL = "managerial"


class InterviewState(StrEnum):
    """Interview lifecycle states."""

    CREATED = "created"
    INTRODUCTION = "introduction"
    QUESTIONING = "questioning"
    FOLLOW_UP = "follow_up"
    DEEP_DIVE = "deep_dive"
    CLOSING = "closing"
    COMPLETED = "completed"
    
    # DSA States
    PROBLEM_PRESENTATION = "problem_presentation"
    UNDERSTANDING = "understanding"
    APPROACH = "approach"
    OPTIMIZATION = "optimization"


class InterviewEvent(StrEnum):
    """Events that can change interview state."""

    START = "start"
    INTRODUCTION_COMPLETE = "introduction_complete"
    ANSWER_RECEIVED = "answer_received"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    DEEP_DIVE_REQUIRED = "deep_dive_required"
    QUESTION_COMPLETE = "question_complete"
    END = "end"
    
    # DSA Events
    PRESENT_PROBLEM = "present_problem"
    MOVE_TO_UNDERSTANDING = "move_to_understanding"
    MOVE_TO_APPROACH = "move_to_approach"
    MOVE_TO_OPTIMIZATION = "move_to_optimization"
    NEXT_PROBLEM = "next_problem"

class InterviewAction(StrEnum):
    """Action selected after evaluating an answer."""

    ASK_FOLLOW_UP = "ask_follow_up"
    DEEP_DIVE = "deep_dive"
    MOVE_ON = "move_on"
    END_INTERVIEW = "end_interview"