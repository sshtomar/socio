"""
FastAPI control plane for orchestrating Modal-backed Marimo sessions.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core import (
    LocalNotebookStorage,
    ModalSessionClient,
    SessionManager,
    get_settings,
)
from core.exceptions import SessionOrchestratorError, WorkspaceNotFound
from schemas import (
    WorkspaceCreateRequest,
    WorkspaceResponse,
    WorkspaceStatusResponse,
    WorkspaceTerminateResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("session-orchestrator")

settings = get_settings()
storage = LocalNotebookStorage(settings.workspace_storage_root)
modal_client = ModalSessionClient(settings)
manager = SessionManager(settings, storage, modal_client)

app = FastAPI(
    title="Socio Session Orchestrator",
    version="0.1.0",
    description="Control plane for launching Modal-backed Marimo notebooks",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "session-orchestrator"}


@app.post("/workspaces", response_model=WorkspaceResponse)
async def create_workspace(payload: WorkspaceCreateRequest) -> WorkspaceResponse:
    try:
        record = manager.create_session(
            workspace_id=payload.workspace_id,
            requirements=payload.requirements,
            env=payload.env,
            metadata=payload.metadata,
            notebook_filename=payload.notebook_filename,
        )
        return WorkspaceResponse.from_session(record)
    except SessionOrchestratorError as exc:
        logger.exception("Failed to create workspace")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/workspaces/{workspace_id}", response_model=WorkspaceStatusResponse)
async def get_workspace(workspace_id: str) -> WorkspaceStatusResponse:
    try:
        record = manager.get_session(workspace_id)
        return WorkspaceStatusResponse.from_session(record)
    except WorkspaceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/workspaces", response_model=List[WorkspaceStatusResponse])
async def list_workspaces() -> List[WorkspaceStatusResponse]:
    sessions = manager.list_sessions()
    return [WorkspaceStatusResponse.from_session(record) for record in sessions.values()]


@app.delete("/workspaces/{workspace_id}", response_model=WorkspaceTerminateResponse)
async def terminate_workspace(workspace_id: str) -> WorkspaceTerminateResponse:
    try:
        record = manager.terminate_session(workspace_id)
        return WorkspaceTerminateResponse.from_session(record)
    except WorkspaceNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionOrchestratorError as exc:
        logger.exception("Failed to terminate workspace")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
