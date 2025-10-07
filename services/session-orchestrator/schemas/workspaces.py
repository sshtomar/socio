"""
Workspace request/response models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

from core.models import SessionRecord, SessionStatus


class WorkspaceCreateRequest(BaseModel):
    """Request payload for launching a workspace session."""

    workspace_id: Optional[str] = None
    notebook_filename: str = "main.py"
    requirements: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceResponse(BaseModel):
    """API response for workspace launch."""

    workspace_id: str
    sandbox_id: str
    url: Optional[HttpUrl] = None
    token: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_session(cls, record: SessionRecord) -> "WorkspaceResponse":
        data = {
            "workspace_id": record.workspace_id,
            "sandbox_id": record.sandbox_id,
            "url": record.url,
            "token": record.token,
            "status": record.status,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "metadata": record.metadata,
        }
        return cls(**data)


class WorkspaceStatusResponse(BaseModel):
    """Status payload for existing sessions."""

    workspace_id: str
    status: SessionStatus
    url: Optional[HttpUrl] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_session(cls, record: SessionRecord) -> "WorkspaceStatusResponse":
        return cls(
            workspace_id=record.workspace_id,
            status=record.status,
            url=record.url,
            metadata=record.metadata,
        )


class WorkspaceTerminateResponse(BaseModel):
    """Response returned when a workspace is terminated."""

    workspace_id: str
    status: SessionStatus
    terminated: bool

    @classmethod
    def from_session(cls, record: SessionRecord) -> "WorkspaceTerminateResponse":
        return cls(
            workspace_id=record.workspace_id,
            status=record.status,
            terminated=record.status == SessionStatus.terminated,
        )
