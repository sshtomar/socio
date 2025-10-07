# Architecture Overview

## Core Components
- **Gateway**: Handles OAuth login, session validation, and routes traffic to internal services. Starts as a thin FastAPI/Express service backed by Auth0 (or Clerk).
- **Workspace API**: Wraps managed database + object storage (Supabase/Firebase). Stores projects, notebook manifests, and environment metadata.
- **Session Orchestrator**: Calls managed notebook runners (Modal, Replicate, etc.) to spin marimo sessions. Tracks lifecycle events and ensures user volumes mount correctly.
- **Coding Agent**: LLM-powered helper exposed via REST/WebSocket. Uses hosted models initially, with prompts and tools centralized in `packages/agent-sdk`.
- **Notebook App**: Marimo server wrapper plus dashboard shell that talks to Workspace API and Session Orchestrator.
- **Landing App**: Public marketing site with sign-up funnel.

## Shared Packages
- `agent-sdk`: Prompt templates, evaluation utilities, and client helpers consumed by both notebooks and the agent service.
- `ui-components`: Reusable React components for landing and dashboard experiences.

## Infrastructure
- Managed providers supply auth, database, storage, and runtime during MVP.
- `infra/terraform` and `infra/k8s` house infrastructure-as-code snippets for future self-hosted deployments.
- `env/` stores configuration templates documenting required environment variables per service.

## Data Flow (MVP)
1. User authenticates via Auth0; gateway issues signed session token.
2. Dashboard requests project metadata from Workspace API (backed by Supabase).
3. Starting a notebook triggers Session Orchestrator to request a new marimo instance from managed runtime provider.
4. Notebook persists files through Workspace API to object storage; autosave diffs happen asynchronously.
5. Coding Agent receives cell context via REST call from Notebook App and returns suggested code.

## Future Considerations
- Replace managed runtime with self-hosted Kubernetes when concurrency or cost requires.
- Introduce event bus (e.g., NATS) for autosave, snapshot, and agent auditing events.
- Partition services into separate repos when release cadences diverge or compliance demands isolation.

