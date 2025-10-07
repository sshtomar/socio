# Socio

Socio is an early-stage platform that lets social scientists build and resume impact evaluation workflows using marimo notebooks.

## Monorepo layout

- `apps/landing`: marketing site and authentication entry point.
- `apps/notebook-app`: marimo wrapper and dashboard shell.
- `services/gateway`: API gateway and auth glue.
- `services/workspace-api`: workspace metadata + persistence adapters.
- `services/session-orchestrator`: managed runtime adapters for notebook sessions.
- `services/coding-agent`: LLM-backed coding assistant endpoints.
- `packages/agent-sdk`: shared prompts, evaluation harnesses, and agent client utilities.
- `packages/ui-components`: shared UI primitives.
- `docs`: architecture notes, roadmap, and integration records.
- `infra`: infrastructure-as-code and deployment manifests.
- `env`: environment configuration templates.

## MVP focus

1. Authenticated single-project marimo sessions with durable storage.
2. Thin agent integration via hosted LLM provider.
3. Observability for session lifecycle and autosave events.

## Development quickstart

1. Copy `.env.example` from `env/` once it exists and fill provider keys.
2. Use Docker (or dev containers) per app/service to mirror production environments.
3. Run unit tests with local stubs for third-party services before deploying.

## Next steps

- Select Auth (Auth0/Clerk) and storage (Supabase/Firebase) providers.
- Draft adapter interfaces inside each service.
- Set up CI to lint and test the monorepo.

