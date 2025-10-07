"""
Base agent class with common functionality
"""

from anthropic import Anthropic
from typing import Optional, AsyncIterator, Dict, Any
import logging

from schemas.responses import AgentMessage, MessageType, UsageStats
from schemas.internal import NotebookContext
from core.config import get_settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents"""

    def __init__(
        self,
        system_prompt: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        settings = get_settings()
        self.client = Anthropic(api_key=api_key or settings.anthropic_api_key)
        self.model = model or settings.default_model
        self.system_prompt = system_prompt
        self.max_tokens = settings.max_tokens_per_request

    async def stream_response(
        self,
        messages: list,
        **kwargs
    ) -> AsyncIterator[AgentMessage]:
        """
        Stream responses from Claude with proper message formatting.

        Args:
            messages: List of message dicts
            **kwargs: Additional arguments for API call

        Yields:
            AgentMessage objects
        """
        try:
            # Use non-streaming for now (simpler and works)
            # TODO: Implement proper streaming in future
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                messages=messages,
                **kwargs
            )

            # Extract text content
            text_content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    text_content += block.text

            # Yield the response as a single message
            yield AgentMessage(
                type=MessageType.THINKING,
                content=text_content,
                metadata={"streaming": False}
            )

            # Add usage stats if available
            if response.usage:
                usage = UsageStats(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    total_tokens=(
                        response.usage.input_tokens +
                        response.usage.output_tokens
                    ),
                    estimated_cost_usd=self._calculate_cost(response.usage)
                )

                yield AgentMessage(
                    type=MessageType.USAGE,
                    content=usage.model_dump(),
                    metadata={}
                )

        except Exception as e:
            logger.error(f"Error in response: {e}", exc_info=True)
            yield AgentMessage(
                type=MessageType.ERROR,
                content={"error": str(e)},
                metadata={}
            )

    def _calculate_cost(self, usage) -> float:
        """
        Calculate estimated cost based on token usage.

        Rates for Claude Sonnet 4 (as of Oct 2024):
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        """
        input_cost = (usage.input_tokens / 1_000_000) * 3.0
        output_cost = (usage.output_tokens / 1_000_000) * 15.0
        return round(input_cost + output_cost, 6)

    def _format_context(self, context: NotebookContext) -> str:
        """Format notebook context for inclusion in prompts"""
        parts = []

        if context.variables:
            vars_list = "\n".join(
                f"- {name}: {dtype}"
                for name, dtype in context.variables.items()
            )
            parts.append(f"Available variables:\n{vars_list}")
        else:
            parts.append("No variables currently defined in notebook.")

        if context.last_error:
            parts.append(f"\nRecent error:\n```\n{context.last_error}\n```")

        parts.append(f"\nNotebook has {context.cell_count} cells.")

        return "\n\n".join(parts)
