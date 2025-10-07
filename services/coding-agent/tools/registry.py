"""
Tool registration and MCP server creation
"""

from claude_agent_sdk import create_sdk_mcp_server
from .notebook import (
    inspect_dataframe,
    execute_cell,
    get_variables,
    sample_data,
)


def create_tool_server(name: str = "socio-notebook-tools", version: str = "0.1.0"):
    """
    Create an MCP server with all notebook tools registered.

    Args:
        name: Server name
        version: Server version

    Returns:
        MCP server instance
    """
    server = create_sdk_mcp_server(
        name=name,
        version=version,
        tools=[
            inspect_dataframe,
            execute_cell,
            get_variables,
            sample_data,
        ]
    )

    return server


# Tool descriptions for documentation
TOOL_DESCRIPTIONS = {
    "inspect_dataframe": {
        "name": "inspect_dataframe",
        "description": "Get schema and summary statistics of a dataframe",
        "parameters": {
            "variable_name": "Name of the dataframe variable",
            "notebook_id": "Notebook identifier"
        },
        "returns": "Schema information including columns, dtypes, shape, missing values"
    },
    "sample_data": {
        "name": "sample_data",
        "description": "Get a sample of rows from a dataframe",
        "parameters": {
            "variable_name": "Name of the dataframe variable",
            "n": "Number of rows to sample (default: 5)",
            "method": "'head', 'tail', or 'random' (default: 'head')",
            "notebook_id": "Notebook identifier"
        },
        "returns": "Sample data as JSON"
    },
    "execute_cell": {
        "name": "execute_cell",
        "description": "Execute Python code in the notebook",
        "parameters": {
            "code": "Python code to execute",
            "notebook_id": "Notebook identifier"
        },
        "returns": "Execution result with status, output, errors"
    },
    "get_variables": {
        "name": "get_variables",
        "description": "List all variables in the notebook namespace",
        "parameters": {
            "notebook_id": "Notebook identifier"
        },
        "returns": "Dictionary mapping variable names to their types"
    }
}
