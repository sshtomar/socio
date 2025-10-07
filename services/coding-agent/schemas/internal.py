from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List
from enum import Enum


class QueryRoute(str, Enum):
    """Possible routes for queries"""
    QUICK_FIX = "quick_fix"
    SIMPLE_CODE = "simple_code"
    COMPLEX_EDA = "complex_eda"
    EXPLAIN = "explain"
    STORYTELLING = "storytelling"


class NotebookContext(BaseModel):
    """Internal representation of notebook context"""

    notebook_id: str
    session_id: str
    variables: Dict[str, str] = Field(default_factory=dict)
    last_error: Optional[str] = None
    cell_count: int = 0
    current_cell: Optional[int] = None

    def has_error(self) -> bool:
        """Check if there's a recent error"""
        return self.last_error is not None and len(self.last_error) > 0

    def is_empty(self) -> bool:
        """Check if notebook is empty"""
        return self.cell_count == 0 and len(self.variables) == 0


class ToolResult(BaseModel):
    """Result from a tool execution"""

    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


class CritiqueResult(BaseModel):
    """Result from self-critique"""

    semantic_precision: Dict[str, Any] = Field(
        default_factory=dict,
        description="Issues with semantic precision"
    )
    rhetorical_persuasion: Dict[str, Any] = Field(
        default_factory=dict,
        description="Issues with rhetorical persuasion"
    )
    pragmatic_relevance: Dict[str, Any] = Field(
        default_factory=dict,
        description="Issues with pragmatic relevance"
    )

    @property
    def has_issues(self) -> bool:
        """Check if any dimension has issues"""
        return (
            bool(self.semantic_precision.get("issues")) or
            bool(self.rhetorical_persuasion.get("issues")) or
            bool(self.pragmatic_relevance.get("issues"))
        )

    @property
    def issue_count(self) -> int:
        """Count total issues across all dimensions"""
        count = 0
        count += len(self.semantic_precision.get("issues", []))
        count += len(self.rhetorical_persuasion.get("issues", []))
        count += len(self.pragmatic_relevance.get("issues", []))
        return count
