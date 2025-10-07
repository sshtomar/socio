from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class NotebookContextData(BaseModel):
    """Context about the current notebook state"""

    variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Available variables and their types"
    )
    last_error: Optional[str] = Field(
        None,
        description="Last error message if any"
    )
    cell_count: int = Field(
        0,
        description="Number of cells in notebook"
    )
    current_cell: Optional[int] = Field(
        None,
        description="Current cell index"
    )
    notebook_id: str = Field(
        ...,
        description="Unique notebook identifier"
    )
    session_id: str = Field(
        ...,
        description="Session identifier for tracking insights"
    )


class QueryRequest(BaseModel):
    """Request for agent query with streaming support"""

    query: str = Field(
        ...,
        description="User's query or request"
    )
    context: NotebookContextData = Field(
        ...,
        description="Current notebook context"
    )
    require_high_quality: bool = Field(
        default=False,
        description="Whether to use self-critique for higher quality (slower, more expensive)"
    )
    api_key: Optional[str] = Field(
        None,
        description="Optional user-provided API key to override default"
    )


class QuickQueryRequest(BaseModel):
    """Request for non-streaming quick queries"""

    query: str = Field(
        ...,
        description="User's query or request"
    )
    context: NotebookContextData = Field(
        ...,
        description="Current notebook context"
    )
    api_key: Optional[str] = Field(
        None,
        description="Optional user-provided API key"
    )


class StreamMessage(BaseModel):
    """Message types for WebSocket streaming"""

    type: str = Field(
        ...,
        description="Message type: query, approval, cancel"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Message payload"
    )


class ApprovalResponse(BaseModel):
    """User's response to a plan approval request"""

    approved: bool = Field(
        ...,
        description="Whether user approved the plan"
    )
    modifications: Optional[str] = Field(
        None,
        description="User's requested modifications to the plan"
    )
