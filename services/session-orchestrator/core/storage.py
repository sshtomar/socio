"""
Notebook storage adapters for the orchestrator.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Iterable
import json

from .exceptions import StorageError


class NotebookStorage(ABC):
    """Interface for persisting workspace notebooks and metadata."""

    @abstractmethod
    def ensure_workspace(self, workspace_id: str) -> Path:
        """Return a writable path for the workspace, creating it if needed."""

    @abstractmethod
    def persist_requirements(self, workspace_id: str, requirements: Iterable[str]) -> Path:
        """Persist requirements for downstream uv sync."""

    @abstractmethod
    def persist_metadata(self, workspace_id: str, metadata: Dict) -> Path:
        """Persist metadata about the workspace runtime."""


class LocalNotebookStorage(NotebookStorage):
    """Filesystem-backed storage adapter for local development."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def ensure_workspace(self, workspace_id: str) -> Path:
        try:
            workspace_path = self.root / workspace_id
            workspace_path.mkdir(parents=True, exist_ok=True)
            return workspace_path
        except OSError as exc:
            raise StorageError(f"Failed to create workspace directory for {workspace_id}") from exc

    def persist_requirements(self, workspace_id: str, requirements: Iterable[str]) -> Path:
        workspace_path = self.ensure_workspace(workspace_id)
        requirements_path = workspace_path / "requirements.txt"
        try:
            requirements_list = list(requirements)
            content = "\n".join(requirements_list)
            if content:
                content += "\n"
            requirements_path.write_text(content)
            return requirements_path
        except OSError as exc:
            raise StorageError("Failed to write requirements.txt") from exc

    def persist_metadata(self, workspace_id: str, metadata: Dict) -> Path:
        workspace_path = self.ensure_workspace(workspace_id)
        metadata_path = workspace_path / "workspace.json"
        try:
            metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))
            return metadata_path
        except OSError as exc:
            raise StorageError("Failed to write workspace metadata") from exc
