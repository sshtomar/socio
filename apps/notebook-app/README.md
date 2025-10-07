# Notebook App

Wrapper around marimo notebook server plus lightweight dashboard.

MVP Responsibilities:
- Authenticate user session via gateway.
- Request notebook sessions from Session Orchestrator and embed marimo UI.
- Trigger autosave snapshots and agent assistance requests.

Implementation Notes:
- Start with Python entrypoint that configures marimo server and proxies API calls.
- Use env templates from `env/notebook-app.env.example` (to be added) for service URLs and tokens.

