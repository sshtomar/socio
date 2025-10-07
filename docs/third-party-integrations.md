# Third-Party Integrations

| Capability        | Provider (MVP) | Notes |
|-------------------|----------------|-------|
| Authentication    | Auth0 / Clerk  | OAuth + RBAC; store domain, client ID, audience in `env/gateway.env.example`. |
| Database + Storage| Supabase       | Postgres for metadata, object storage for notebooks; service key kept in secrets manager. |
| Notebook Runtime  | Modal / Replicate | Creates marimo containers on demand; orchestrator stores session ID + status. |
| LLM Provider      | OpenAI / Anthropic | Used by coding agent; configure API key and model defaults in `env/coding-agent.env.example`. |
| Observability     | Logtail / Datadog | Ship logs + metrics from services and notebook sessions for debugging. |

## Migration Notes
- Each integration is abstracted behind adapters inside its service to allow swapping providers without touching consumers.
- Maintain least-privilege API keys and document rotation cadence within `env/` templates.

