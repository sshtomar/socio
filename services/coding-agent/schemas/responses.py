from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class MessageType(str, Enum):
    """Types of messages that can be streamed"""
    THINKING = "thinking"
    PLAN = "plan"
    APPROVAL_NEEDED = "approval_needed"
    CODE = "code"
    EXECUTION_RESULT = "execution_result"
    EXPLANATION = "explanation"
    ERROR = "error"
    COMPLETE = "complete"
    USAGE = "usage"


class AgentMessage(BaseModel):
    """Single message in agent response stream"""

    type: MessageType = Field(
        ...,
        description="Type of message"
    )
    content: Any = Field(
        ...,
        description="Message content"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class PlanStep(BaseModel):
    """A single step in an analysis plan"""

    step_number: int
    description: str
    rationale: Optional[str] = None
    estimated_time: Optional[str] = None


class PlanResponse(BaseModel):
    """Response containing an analysis plan"""

    title: str = Field(
        ...,
        description="Brief title of the analysis"
    )
    steps: List[PlanStep] = Field(
        ...,
        description="Ordered list of analysis steps"
    )
    expected_outputs: List[str] = Field(
        default_factory=list,
        description="What outputs user can expect"
    )
    requires_approval: bool = Field(
        default=True,
        description="Whether this plan needs user approval"
    )


class ExecutionResult(BaseModel):
    """Result of code execution"""

    status: str = Field(
        ...,
        description="success, error, or warning"
    )
    code: str = Field(
        ...,
        description="Code that was executed"
    )
    output: Optional[str] = Field(
        None,
        description="Standard output"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if any"
    )
    execution_time_ms: Optional[int] = Field(
        None,
        description="Execution time in milliseconds"
    )


class ExecutionResponse(BaseModel):
    """Response containing execution results"""

    results: List[ExecutionResult] = Field(
        ...,
        description="Results of executed steps"
    )
    explanation: Optional[str] = Field(
        None,
        description="Explanation of results"
    )
    insights: List[str] = Field(
        default_factory=list,
        description="Key insights from the analysis"
    )


class UsageStats(BaseModel):
    """Token usage statistics"""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class AgentResponse(BaseModel):
    """Complete agent response"""

    query: str = Field(
        ...,
        description="Original query"
    )
    route: str = Field(
        ...,
        description="Route taken (quick_fix, simple_code, etc.)"
    )
    messages: List[AgentMessage] = Field(
        default_factory=list,
        description="Stream of messages"
    )
    usage: Optional[UsageStats] = Field(
        None,
        description="Token usage statistics"
    )
    session_id: str = Field(
        ...,
        description="Session identifier"
    )
