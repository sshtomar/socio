"""
Custom exceptions for the session orchestrator.
"""


class SessionOrchestratorError(Exception):
    """Base error class for orchestrator failures."""


class WorkspaceNotFound(SessionOrchestratorError):
    """Raised when the requested workspace does not exist."""


class ModalInteractionError(SessionOrchestratorError):
    """Raised when the call to Modal fails."""


class StorageError(SessionOrchestratorError):
    """Raised when notebook storage operations fail."""
