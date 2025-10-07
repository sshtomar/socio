# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Socio is a platform for social scientists to build and resume impact evaluation workflows using marimo notebooks. The architecture uses managed third-party providers (Auth0/Clerk, Supabase, Modal/Replicate, OpenAI/Anthropic) during MVP phase, with adapter patterns enabling future migration to self-hosted infrastructure.

## Monorepo Structure

**Apps:**
- `apps/landing`: Marketing site and authentication entry point
- `apps/notebook-app`: Marimo wrapper and dashboard shell

**Services:**
- `services/gateway`: API gateway handling OAuth validation, session management, and request routing
- `services/workspace-api`: Workspace metadata persistence, notebook storage via Supabase
- `services/session-orchestrator`: Manages marimo runtime lifecycle via Modal/Replicate
- `services/coding-agent`: LLM-backed coding assistant using hosted providers

**Packages:**
- `packages/agent-sdk`: Shared prompt templates, evaluation harnesses, and agent client utilities consumed by both notebooks and the agent service
- `packages/ui-components`: Shared React components for frontend apps

**Other:**
- `docs/`: Architecture notes, roadmap, and integration records
- `infra/`: Infrastructure-as-code (Terraform modules, K8s manifests) for managed service setup and future self-hosted deployments
- `env/`: Environment configuration templates documenting required variables per service

## Architecture Principles

### Adapter Pattern
Each third-party integration is abstracted behind service-specific adapters to enable provider swapping without affecting consumers. Key integration points:
- **Authentication**: Auth0/Clerk (gateway service)
- **Database + Storage**: Supabase (workspace-api service)
- **Notebook Runtime**: Modal/Replicate (session-orchestrator service)
- **LLM Provider**: OpenAI/Anthropic (coding-agent service)

### Data Flow (MVP)
1. User authenticates via Auth0 → gateway issues signed session token
2. Dashboard requests project metadata from workspace-api (Supabase-backed)
3. Starting a notebook triggers session-orchestrator to request marimo instance from managed runtime
4. Notebook persists files through workspace-api to object storage; autosave diffs happen asynchronously
5. Coding agent receives cell context via REST from notebook-app and returns suggested code

## Development Setup

### Environment Configuration
1. Copy service-specific templates from `env/` directory (when available)
2. Fill in provider keys and service URLs in local `.env` files
3. Keep secrets out of version control

### Docker Usage
Use Docker or dev containers per app/service to mirror production environments. Each service should have its own container configuration.

### Testing
Run unit tests with local stubs for third-party services before deploying. Stubs should implement the same adapter interfaces as production providers.

## Migration Considerations

Future phases may involve:
- Replacing managed runtime with self-hosted Kubernetes
- Introducing event bus (NATS) for autosave, snapshot, and agent auditing
- Partitioning services into separate repos when release cadences diverge

Infrastructure code in `infra/` should remain modular to support smooth migration paths.
