"""
Session manager orchestrating storage and Modal interactions.
"""

from __future__ import annotations

import secrets
import threading
import uuid
from typing import Dict, Iterable, Optional

from .config import Settings
from .exceptions import SessionOrchestratorError, WorkspaceNotFound
from .modal_client import ModalSessionClient
from .models import SessionRecord, WorkspaceSpec
from .storage import NotebookStorage


class SessionManager:
    """High-level API for workspace session lifecycle management."""

    def __init__(
        self,
        settings: Settings,
        storage: NotebookStorage,
        modal_client: ModalSessionClient,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.modal_client = modal_client
        self._sessions: Dict[str, SessionRecord] = {}
        self._lock = threading.Lock()

    def create_session(
        self,
        workspace_id: Optional[str] = None,
        requirements: Optional[Iterable[str]] = None,
        env: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None,
        notebook_filename: Optional[str] = None,
    ) -> SessionRecord:
        ws_id = workspace_id or self._generate_workspace_id()
        token = self._generate_token()
        requirements = list(requirements or [])
        env = dict(env or {})
        metadata = dict(metadata or {})
        notebook_filename = notebook_filename or "main.py"

        workspace_path = self.storage.ensure_workspace(ws_id)

        self.storage.persist_requirements(ws_id, requirements)
        self.storage.persist_metadata(
            ws_id,
            {
                "workspace_id": ws_id,
                "notebook_filename": notebook_filename,
                "requirements": requirements,
                "env": env,
                "metadata": metadata,
            },
        )

        spec = WorkspaceSpec(
            workspace_id=ws_id,
            token=token,
            notebook_filename=notebook_filename,
            requirements=requirements,
            env=env,
            metadata=metadata | {"workspace_path": str(workspace_path)},
        )

        record = self.modal_client.launch_session(spec)

        with self._lock:
            self._sessions[ws_id] = record

        return record

    def get_session(self, workspace_id: str) -> SessionRecord:
        with self._lock:
            if workspace_id not in self._sessions:
                raise WorkspaceNotFound(f"No workspace found for id {workspace_id}")
            return self._sessions[workspace_id]

    def list_sessions(self) -> Dict[str, SessionRecord]:
        with self._lock:
            return dict(self._sessions)

    def terminate_session(self, workspace_id: str) -> SessionRecord:
        with self._lock:
            if workspace_id not in self._sessions:
                raise WorkspaceNotFound(f"No workspace found for id {workspace_id}")
            record = self._sessions[workspace_id]

        self.modal_client.stop_session(record)

        with self._lock:
            self._sessions[workspace_id] = record

        return record

    def _generate_workspace_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def _generate_token(self) -> str:
        length = max(self.settings.modal_token_length, 8)
        return secrets.token_urlsafe(length)
