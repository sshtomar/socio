# Gateway Service

Responsibilities:
- Validate OAuth tokens from Auth0/Clerk and issue internal session cookies.
- Proxy requests to Workspace API and Session Orchestrator.
- Provide a unified entry point for the notebook app and landing auth callbacks.

MVP Stack:
- FastAPI (Python) or Express (Node) with minimal middlewares.
- Adapter interfaces for auth provider and rate limiting.

Next Steps:
- Define request/response contracts for downstream services.
- Implement local stub auth provider for development.

