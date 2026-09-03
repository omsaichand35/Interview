class InterviewOSException(Exception):
    """Base exception for InterviewOS."""

    pass


class DocumentProcessingError(InterviewOSException):
    """Raised when a document cannot be loaded or processed."""

    pass


class AnalysisError(InterviewOSException):
    """Raised when document analysis fails."""

    pass


class LLMError(InterviewOSException):
    """Raised when an LLM operation fails."""

    pass


class RAGError(InterviewOSException):
    """Raised when a RAG operation fails."""

    pass


class ConfigurationError(InterviewOSException):
    """Raised when application configuration is invalid."""

    pass


class LLMUnavailableError(LLMError):
    """Raised when the LLM is completely unreachable or times out."""

    pass


class LLMRateLimitError(LLMError):
    """Raised when the LLM provider returns a rate limit error (HTTP 429)."""

    pass


class InvalidLLMResponseError(LLMError):
    """Raised when the LLM response cannot be validated after retries."""

    pass


class InterviewStateError(InterviewOSException):
    """Raised when an invalid state transition is attempted."""

    pass


class OrchestratorError(InterviewOSException):
    """Raised when the orchestrator fails to manage the interview flow."""

    pass