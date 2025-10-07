"""
Dataclasses and enums used by the orchestrator core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SessionStatus(str, Enum):
    """Lifecycle states for a Modal sandbox session."""

    pending = "pending"
    provisioning = "provisioning"
    running = "running"
    terminated = "terminated"
    failed = "failed"


@dataclass
class WorkspaceSpec:
    """Configuration required to launch a workspace session."""

    workspace_id: str
    token: str
    notebook_filename: str
    requirements: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionRecord:
    """Internal record of a Modal sandbox session."""

    workspace_id: str
    sandbox_id: str
    token: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    status: SessionStatus = SessionStatus.pending
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_provisioning(self) -> None:
        self.status = SessionStatus.provisioning
        self.updated_at = datetime.utcnow()

    def mark_running(self, url: str) -> None:
        self.status = SessionStatus.running
        self.url = url
        self.updated_at = datetime.utcnow()

    def mark_terminated(self) -> None:
        self.status = SessionStatus.terminated
        self.updated_at = datetime.utcnow()

    def mark_failed(self, reason: str) -> None:
        self.status = SessionStatus.failed
        self.metadata["failure_reason"] = reason
        self.updated_at = datetime.utcnow()
