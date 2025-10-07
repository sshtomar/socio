"""
Quick executor agent for fast, simple queries
"""

from typing import AsyncIterator
import logging

from .base import BaseAgent
from schemas.responses import AgentMessage, MessageType
from schemas.internal import NotebookContext
from prompts.system_prompts import QUICK_EXECUTOR_PROMPT

logger = logging.getLogger(__name__)


class QuickExecutor(BaseAgent):
    """Agent for quick fixes and simple code generation (1-3 second responses)"""

    def __init__(self, **kwargs):
        super().__init__(
            system_prompt=QUICK_EXECUTOR_PROMPT,
            **kwargs
        )

    async def execute(
        self,
        query: str,
        context: NotebookContext
    ) -> AsyncIterator[AgentMessage]:
        """
        Execute a quick query and stream results.

        Args:
            query: User's query
            context: Notebook context

        Yields:
            AgentMessage objects
        """
        try:
            # Format context
            context_str = self._format_context(context)

            # Build messages
            user_message = f"""{context_str}

User request: {query}

Provide a quick, direct response. For code generation, output executable Python code.
For fixes, identify the issue and provide the corrected code."""

            messages = [
                {
                    "role": "user",
                    "content": user_message
                }
            ]

            # Stream response
            async for message in self.stream_response(messages):
                yield message

            # Send completion signal
            yield AgentMessage(
                type=MessageType.COMPLETE,
                content={"status": "success"},
                metadata={}
            )

        except Exception as e:
            logger.error(f"Error in quick executor: {e}", exc_info=True)
            yield AgentMessage(
                type=MessageType.ERROR,
                content={"error": str(e)},
                metadata={}
            )
