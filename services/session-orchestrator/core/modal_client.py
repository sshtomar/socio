"""
Thin wrapper around the Modal Python SDK.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import timedelta
from typing import Any, Dict

from .config import Settings
from .exceptions import ModalInteractionError
from .models import SessionRecord, SessionStatus, WorkspaceSpec

logger = logging.getLogger(__name__)


class ModalSessionClient:
    """Handles lifecycle management of Modal sandboxes."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._modal = self._import_modal()

    def _import_modal(self):
        try:
            import modal  # type: ignore

            return modal
        except ImportError:
            logger.warning(
                "modal package not installed; sandbox operations will use stub responses"
            )
            return None

    def launch_session(self, spec: WorkspaceSpec) -> SessionRecord:
        """Launch a new Modal sandbox for the workspace."""

        sandbox_id = uuid.uuid4().hex
        record = SessionRecord(workspace_id=spec.workspace_id, sandbox_id=sandbox_id, token=spec.token)
        record.mark_provisioning()

        if self._modal is None:
            # Local development fallback
            stub_url = self._build_stub_url(sandbox_id)
            record.metadata["stub_mode"] = True
            record.mark_running(stub_url)
            return record

        try:
            modal = self._modal

            volume_map: Dict[str, Any] = {}
            if self.settings.modal_volume_notebooks:
                volume_map["/data"] = modal.Volume.from_name(
                    self.settings.modal_volume_notebooks, create_if_missing=True
                )
            if self.settings.modal_volume_cache:
                volume_map["/cache"] = modal.Volume.from_name(
                    self.settings.modal_volume_cache, create_if_missing=True
                )

            timeout = timedelta(seconds=self.settings.modal_timeout_seconds)

            launch_kwargs = {
                "args": [
                    spec.workspace_id,
                    spec.token,
                    spec.notebook_filename,
                ],
                "volumes": volume_map,
                "timeout": timeout,
                "env": spec.env,
                "metadata": spec.metadata | {"workspace_id": spec.workspace_id},
            }

            # Get or create Modal App
            app = modal.App.lookup(self.settings.modal_app_name, create_if_missing=True)

            # Create image with marimo and uv
            image = modal.Image.debian_slim().pip_install("marimo", "uv")

            # Create sandbox with marimo server as entrypoint
            # encrypted_ports creates an HTTPS tunnel URL for the gateway to proxy to
            # Use shell wrapper to ensure directory exists and create initial notebook
            workspace_dir = f"/data/{spec.workspace_id}"
            notebook_path = f"{workspace_dir}/{spec.notebook_filename}"

            # Create a valid marimo notebook if it doesn't exist
            startup_script = (
                f"mkdir -p {workspace_dir} && "
                f"cd {workspace_dir} && "
                f"if [ ! -f {spec.notebook_filename} ]; then "
                f"cat > {spec.notebook_filename} << 'NOTEBOOK_EOF'\n"
                f"import marimo\n\n"
                f"__generated_with = \"0.16.5\"\n"
                f"app = marimo.App()\n\n"
                f"@app.cell\n"
                f"def __():\n"
                f"    import marimo as mo\n"
                f"    return mo,\n\n"
                f"if __name__ == \"__main__\":\n"
                f"    app.run()\n"
                f"NOTEBOOK_EOF\n"
                f"fi && "
                f"marimo edit {spec.notebook_filename} --host 0.0.0.0 --port 8000 --token-password {spec.token}"
            )

            sandbox = modal.Sandbox.create(
                "sh", "-c", startup_script,
                app=app,
                image=image,
                volumes=volume_map,
                timeout=int(timeout.total_seconds()),
                encrypted_ports=[8000],
            )

            sandbox_identifier = getattr(sandbox, "object_id", sandbox_id)
            record.sandbox_id = sandbox_identifier
            record.metadata["modal_sandbox_handle"] = sandbox_identifier

            # Get tunnel URL for encrypted port 8000
            tunnels = getattr(sandbox, "tunnels", None)
            url = None
            if tunnels and callable(tunnels):
                try:
                    tunnel_dict = tunnels()
                    tunnel = tunnel_dict.get(8000)
                    if tunnel:
                        # Tunnel object has host and port attributes
                        host = getattr(tunnel, "host", None)
                        port = getattr(tunnel, "port", 443)
                        if host:
                            url = f"https://{host}" if port == 443 else f"https://{host}:{port}"
                            record.metadata["tunnel_host"] = host
                except Exception as e:
                    logger.warning("Failed to extract tunnel URL: %s", e)
                    url = None

            if not url:
                url = self._build_stub_url(record.sandbox_id)
                record.metadata["missing_modal_url"] = True

            record.mark_running(url)
            return record
        except Exception as exc:  # noqa: BLE001
            record.mark_failed(str(exc))
            logger.exception("Failed to launch Modal sandbox for %s", spec.workspace_id)
            raise ModalInteractionError("Modal sandbox launch failed") from exc

    def stop_session(self, record: SessionRecord) -> None:
        """Stop the Modal sandbox associated with a workspace."""

        if self._modal is None:
            record.mark_terminated()
            record.metadata["stub_terminated"] = True
            return

        try:
            modal = self._modal

            # Get sandbox by ID and terminate it
            sandbox = modal.Sandbox.from_id(record.sandbox_id)
            sandbox.terminate()

            record.mark_terminated()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to stop Modal sandbox %s", record.sandbox_id)
            raise ModalInteractionError("Failed to stop sandbox") from exc

    def _build_stub_url(self, sandbox_id: str) -> str:
        host = os.getenv("LOCAL_SANDBOX_HOST", "http://localhost:8866")
        return f"{host}/workspaces/{sandbox_id}"
