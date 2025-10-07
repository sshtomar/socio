# Infrastructure

This directory houses IaC and deployment configuration for Socio.

Structure:
- `terraform/`: Modules and stacks for managed service wiring (Auth0, Supabase, runtime provider).
- `k8s/`: Helm charts or manifests for future self-hosted deployments.

During MVP, focus on documenting managed service setup and keeping modules modular so migration to self-hosted control plane is straightforward.

