Implementation detail about **Molab’s actual architecture**, and it confirms that what we were planning (Marimo + Modal + R2 + uv) is *exactly* what the Molab team did.

Here’s a **technical implementation plan** for building a self-hosted version of Molab using the same ideas — but adapted for maintainability, cost control, and optional team-only usage.

---

## 🧭 1. High-Level Architecture

**Goal:**
Self-hosted “Marimo Cloud” (Molab-style) that spins up isolated, persistent Marimo notebooks on demand.

**Core Stack (based on HN + Marimo blog)**

| Layer                     | Technology                                     | Role                                                       |
| ------------------------- | ---------------------------------------------- | ---------------------------------------------------------- |
| **Frontend/UI**           | Marimo web editor (`marimo edit`)              | Notebook runtime (browser client + WebSocket backend)      |
| **Backend orchestration** | **Modal Sandboxes**                            | Launch isolated compute per notebook/workspace             |
| **Dependency management** | **uv**                                         | Fast Python environment creation (cached via Modal Volume) |
| **Storage**               | **Cloudflare R2 (S3 API)** or Modal Volume     | Persistent notebook storage                                |
| **Observability**         | **Pydantic Logfire** (optional)                | Application monitoring & logs                              |
| **Auth / Share model**    | “Public but undiscoverable” links + token auth | Same as Molab’s “secret Gist” design                       |

---

## ⚙️ 2. Modal Infrastructure Setup

1. **Modal App & Environment**

   ```bash
   modal app new marimo-cloud
   ```

   Base image:

   ```python
   base_image = (
       modal.Image.debian_slim()
       .apt_install("git", "curl")
       .pip_install("marimo", "uv", "fastapi[standard]", "boto3", "pydantic-logfire")
   )
   ```

2. **Persistent Volumes**

   * `/data/notebooks` – stores notebook files.
   * `/data/uv-cache` – uv cache to accelerate future sandbox launches.

   ```python
   NOTEBOOKS = modal.Volume.from_name("marimo-notebooks", create_if_missing=True)
   CACHE = modal.Volume.from_name("marimo-uv-cache", create_if_missing=True)
   ```

---

## 🧩 3. Control Plane (API Gateway)

**Runs as one always-on FastAPI ASGI service** inside Modal.

Functions:

* Create/Delete workspaces
* Upload/download notebooks
* Spawn Modal Sandboxes
* Return share URLs and token passwords

Example (simplified):

```python
@app.function(volumes={"/data": NOTEBOOKS})
@modal.asgi_app()
def control_plane():
    from fastapi import FastAPI, UploadFile
    import secrets, modal

    api = FastAPI()
    sandboxes = {}

    @api.post("/workspaces")
    def create_ws():
        ws_id = secrets.token_hex(6)
        token = secrets.token_hex(12)
        sandbox = modal.Sandbox.create(
            "run_marimo",
            args=[ws_id, token],
            timeout=7200,
            image=base_image,
            volumes={"/data": NOTEBOOKS, "/cache": CACHE},
        )
        sandboxes[ws_id] = sandbox
        return {"id": ws_id, "url": sandbox.url, "token": token}

    @api.post("/upload/{ws_id}")
    async def upload(ws_id: str, file: UploadFile):
        dest = f"/data/{ws_id}/{file.filename}"
        NOTEBOOKS.write_file(dest, await file.read())
        return {"status": "uploaded", "path": dest}

    @api.delete("/workspaces/{ws_id}")
    def stop(ws_id: str):
        sb = sandboxes.pop(ws_id, None)
        if sb:
            sb.stop()
        return {"status": "terminated"}

    return api
```

---

## 🧮 4. Sandbox Runtime (Marimo Backend)

This is the code that runs *inside* each Modal Sandbox.

```python
@app.function(volumes={"/data": NOTEBOOKS, "/cache": CACHE})
def run_marimo(ws_id: str, token: str):
    import subprocess, pathlib, os
    root = pathlib.Path(f"/data/{ws_id}")
    root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = "/cache"
    subprocess.run(["uv", "sync"], cwd=str(root), env=env)
    subprocess.run([
        "marimo", "edit", f"{root}/main.py",
        "--host", "0.0.0.0", "--port", "8000",
        "--token-password", token
    ])
```

Each sandbox hosts a Marimo instance on port 8000 and exposes it through a **Modal Tunnel**.

---

## ☁️ 5. Persistent Storage (R2 or Modal Volume)

* **Option A (simpler)**: use Modal Volumes (`NOTEBOOKS`) for all persistence.
* **Option B (scalable)**: mount Cloudflare R2 via S3 API.

```python
import boto3, os
r2 = boto3.client(
    "s3",
    endpoint_url="https://<r2-account-id>.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv("R2_KEY"),
    aws_secret_access_key=os.getenv("R2_SECRET")
)
```

All notebooks saved to `/data/notebooks` are uploaded to R2 nightly (or upon shutdown).

---

## 🔐 6. Auth & Access Model

* Default: **“public but undiscoverable”** URLs (as in Molab).
* Add token-based protection using Marimo’s `--token-password`.
* Optional: integrate **Modal Proxy Auth Tokens** for private deployments.
* Recommended: disable crawler indexing (`robots.txt` + meta noindex).

**Important:** as noted in the HN comments, robots.txt alone is insufficient; use signed URLs or Modal-side auth middleware.

---

## 🧰 7. Monitoring (optional)

Integrate [Pydantic Logfire](https://logfire.pydantic.dev):

```python
from logfire import logfire
logfire.configure(api_key=os.getenv("LOGFIRE_KEY"))
logfire.info("Workspace started", ws_id=ws_id)
```

This gives visibility into sandbox launches, errors, and runtime performance.

---

## ⚙️ 8. Operations

| Task             | Mechanism                                           |
| ---------------- | --------------------------------------------------- |
| **Startup**      | Modal auto-spawns sandbox on `/workspaces` call     |
| **Idle timeout** | Modal `timeout` (e.g. 2 h) automatically tears down |
| **Autoscaling**  | Each workspace = one sandbox → fully elastic        |
| **Cost control** | Volume-based persistence + shared `uv` cache        |
| **Cleanup**      | Nightly cron to delete expired workspaces           |

---

## 💰 9. Cost Model (rough)

| Usage pattern                      | Expected monthly                       |
| ---------------------------------- | -------------------------------------- |
| 5 users × 1 core × 2 GB × 2 h/day  | ≈ $10–$15 (fits in free Modal credits) |
| 20 users × 1 core × 4 GB × 4 h/day | ≈ $180–$200                            |
| + R2 storage (~10 GB)              | $1–$2                                  |
| + Logfire monitoring               | free tier → $0                         |

Scales linearly with active notebooks; idle sandboxes cost $0.

---

## 🧪 10. Local Development Workflow

1. `modal serve control_plane.py` — test API locally.
2. `curl -X POST /workspaces` → returns sandbox URL.
3. `curl -F "file=@nb.py" /upload/{id}` → push notebook.
4. Visit tunnel URL → open Marimo UI.

---

## 📦 11. Extensions (Later Phases)

* Real-time collaboration → WebRTC or websocket relay service.
* Team spaces with per-user auth + quotas.
* Billing integration (Stripe API).
* GPU Sandboxes (Modal supports CUDA images).
* Notebook snapshots & versioning.

---

### ✅ Summary

You can think of this as:

> **A control plane (FastAPI + Modal) that spawns ephemeral uv-backed Marimo sandboxes with persistent R2 storage and token-protected sharing.**

It reproduces Molab’s design almost 1-to-1, but you own the deployment, security policy, and cost ceiling.

---
