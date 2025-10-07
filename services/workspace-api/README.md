# Workspace API

Responsibilities:
- Manage users, projects, and notebook metadata.
- Persist notebook files, snapshots, and environment manifests via managed storage.
- Expose REST/GraphQL endpoints for dashboard and notebook clients.

MVP Stack:
- FastAPI or Node + Supabase client.
- Background tasks for autosave batching and snapshot creation.

Next Steps:
- Model initial database schema for projects and notebooks.
- Implement storage adapter interface with Supabase as default.

