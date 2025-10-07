# Session Orchestrator

Responsibilities:
- Request marimo runtime instances from managed providers (Modal sandboxes).
- Track session lifecycle, health, and resource usage.
- Coordinate mounting user storage and injecting environment variables.

## Current implementation

- `FastAPI` control plane (`main.py`) with REST endpoints for session lifecycle.
- In-memory `SessionManager` that coordinates storage and Modal interactions.
- Notebook persistence via `LocalNotebookStorage` (filesystem) to mimic Modal volume/R2 flows.
- `ModalSessionClient` thin wrapper around the Modal SDK with a local stub fallback.
- Pydantic schemas for request/response validation.

## Getting started

1. Install dependencies:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```
2. Set Modal credentials and optional R2 settings in `.env`.
3. Run the API:
   ```bash
   uvicorn main:app --reload --port 8002
   ```

## Next steps

- Replace the in-memory registry with persistent metadata storage (Workspace API or Postgres).
- Wire up Cloudflare R2 syncing for notebook artifacts.
- Add health polling/webhooks to reconcile sandbox status changes from Modal.
- Expand test coverage for error modes and stub implementations.*** End Patch
