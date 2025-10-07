"""
Tools for interacting with notebook runtime via session-orchestrator
"""

import json
import httpx
from typing import Dict, Any, Optional
from claude_agent_sdk import tool
import os


# TODO: This will be replaced with actual session-orchestrator integration
# For now, we'll create stub implementations that can be tested locally


class NotebookRuntime:
    """Client for notebook runtime operations"""

    def __init__(self, orchestrator_url: Optional[str] = None):
        self.base_url = orchestrator_url or os.getenv(
            "SESSION_ORCHESTRATOR_URL",
            "http://localhost:8002"
        )
        self.client = httpx.AsyncClient(timeout=30.0)

    async def eval(self, code: str, notebook_id: str) -> Any:
        """Evaluate expression and return result"""
        # TODO: Implement actual API call to session-orchestrator
        # For now, return stub data
        return {
            "status": "stub",
            "message": "Session orchestrator integration pending",
            "code": code
        }

    async def execute(self, code: str, notebook_id: str) -> Dict[str, Any]:
        """Execute code and return output/errors"""
        # TODO: Implement actual API call
        return {
            "status": "stub",
            "stdout": "Session orchestrator integration pending",
            "stderr": None,
            "duration_ms": 0
        }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global runtime instance
_runtime = NotebookRuntime()


@tool(
    "inspect_dataframe",
    "Get schema and summary statistics of a dataframe without loading full data"
)
async def inspect_dataframe(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inspect a dataframe to get schema, shape, and summary info.

    Args:
        variable_name: Name of the dataframe variable
        notebook_id: Notebook identifier

    Returns:
        Schema information including columns, dtypes, shape, missing values
    """
    var_name = args.get("variable_name")
    notebook_id = args.get("notebook_id")

    if not var_name:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": "variable_name is required"})
            }]
        }

    # Construct inspection code
    inspection_code = f"""
{{
    'shape': {var_name}.shape,
    'columns': list({var_name}.columns) if hasattr({var_name}, 'columns') else None,
    'dtypes': {var_name}.dtypes.to_dict() if hasattr({var_name}, 'dtypes') else None,
    'missing': {var_name}.isnull().sum().to_dict() if hasattr({var_name}, 'isnull') else None,
    'memory_mb': round({var_name}.memory_usage(deep=True).sum() / 1024**2, 2) if hasattr({var_name}, 'memory_usage') else None,
    'index_type': type({var_name}.index).__name__ if hasattr({var_name}, 'index') else None
}}
"""

    result = await _runtime.eval(inspection_code, notebook_id)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "sample_data",
    "Get a sample of rows from a dataframe"
)
async def sample_data(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get sample rows from a dataframe.

    Args:
        variable_name: Name of the dataframe variable
        n: Number of rows to sample (default: 5)
        method: 'head', 'tail', or 'random' (default: 'head')
        notebook_id: Notebook identifier

    Returns:
        Sample data as JSON
    """
    var_name = args.get("variable_name")
    n = args.get("n", 5)
    method = args.get("method", "head")
    notebook_id = args.get("notebook_id")

    if not var_name:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": "variable_name is required"})
            }]
        }

    # Construct sampling code
    if method == "head":
        sample_code = f"{var_name}.head({n}).to_dict('records')"
    elif method == "tail":
        sample_code = f"{var_name}.tail({n}).to_dict('records')"
    elif method == "random":
        sample_code = f"{var_name}.sample({n}).to_dict('records')"
    else:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": f"Unknown method: {method}"})
            }]
        }

    result = await _runtime.eval(sample_code, notebook_id)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }


@tool(
    "execute_cell",
    "Execute Python code in the notebook and return results"
)
async def execute_cell(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute code in the notebook environment.

    Args:
        code: Python code to execute
        notebook_id: Notebook identifier

    Returns:
        Execution result with status, output, errors
    """
    code = args.get("code")
    notebook_id = args.get("notebook_id")

    if not code:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps({"error": "code is required"})
            }]
        }

    result = await _runtime.execute(code, notebook_id)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "status": result.get("status"),
                "output": result.get("stdout"),
                "error": result.get("stderr"),
                "execution_time_ms": result.get("duration_ms")
            }, indent=2)
        }]
    }


@tool(
    "get_variables",
    "List all variables currently available in the notebook namespace"
)
async def get_variables(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get list of available variables in notebook.

    Args:
        notebook_id: Notebook identifier

    Returns:
        Dictionary mapping variable names to their types
    """
    notebook_id = args.get("notebook_id")

    # Get all non-private variables
    variables_code = """
{k: type(v).__name__ for k, v in globals().items()
 if not k.startswith('_') and not callable(v)}
"""

    result = await _runtime.eval(variables_code, notebook_id)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, indent=2)
        }]
    }
