"""
Agent orchestrator - coordinates routing and execution
"""

from typing import AsyncIterator, Optional
import logging

from schemas.responses import AgentMessage
from schemas.internal import NotebookContext, QueryRoute
from .router import QueryRouter
from .session_manager import get_session_manager
from agents import QuickExecutor

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates query routing and agent execution"""

    def __init__(self, api_key: Optional[str] = None):
        self.router = QueryRouter(api_key=api_key)
        self.quick_executor = QuickExecutor(api_key=api_key)
        self.session_manager = get_session_manager()
        # TODO: Add other agents in Phase 2+
        # self.planner = Planner(api_key=api_key)
        # self.executor = Executor(api_key=api_key)
        # self.critic = Critic(api_key=api_key)
        # self.storyteller = Storyteller(api_key=api_key)

    async def handle_query(
        self,
        query: str,
        context: NotebookContext,
        require_high_quality: bool = False
    ) -> AsyncIterator[AgentMessage]:
        """
        Main entry point - routes query and coordinates agent execution.

        Args:
            query: User's query
            context: Notebook context
            require_high_quality: Whether to use self-critique (Phase 3)

        Yields:
            AgentMessage objects
        """
        try:
            # Get or create session
            session = self.session_manager.get_or_create_session(
                context.session_id,
                context.notebook_id
            )

            # Add user query to conversation history
            self.session_manager.add_user_message(context.session_id, query)

            # Update session with current notebook variables
            self.session_manager.update_notebook_state(
                context.session_id,
                context.variables
            )

            # Classify the query
            route = await self.router.classify(query, context)

            logger.info(f"Routing query to: {route.value}")

            # Route to appropriate handler
            # Phase 1: Only quick_executor for all routes
            # Phase 2+: Add specialized routes

            # Collect assistant response for history
            assistant_response = ""

            if route == QueryRoute.QUICK_FIX:
                async for message in self.quick_executor.execute(query, context):
                    if message.type.value == "thinking":
                        assistant_response += message.content
                    yield message

            elif route == QueryRoute.SIMPLE_CODE:
                async for message in self.quick_executor.execute(query, context):
                    if message.type.value == "thinking":
                        assistant_response += message.content
                    yield message

            elif route == QueryRoute.COMPLEX_EDA:
                # TODO: Phase 2 - Add planning workflow
                # For now, fall back to quick executor
                logger.warning(
                    "Complex EDA detected but planner not implemented yet, "
                    "using quick executor"
                )
                async for message in self.quick_executor.execute(query, context):
                    if message.type.value == "thinking":
                        assistant_response += message.content
                    yield message

            elif route == QueryRoute.EXPLAIN:
                # TODO: Phase 2 - Add explainer agent
                async for message in self.quick_executor.execute(query, context):
                    if message.type.value == "thinking":
                        assistant_response += message.content
                    yield message

            elif route == QueryRoute.STORYTELLING:
                # TODO: Phase 4 - Add storyteller agent
                logger.warning(
                    "Storytelling detected but not implemented yet, "
                    "using quick executor"
                )
                async for message in self.quick_executor.execute(query, context):
                    if message.type.value == "thinking":
                        assistant_response += message.content
                    yield message

            # Save assistant response to conversation history
            if assistant_response:
                self.session_manager.add_assistant_message(
                    context.session_id,
                    assistant_response,
                    metadata={"route": route.value}
                )

        except Exception as e:
            logger.error(f"Error in orchestrator: {e}", exc_info=True)
            from schemas.responses import MessageType
            yield AgentMessage(
                type=MessageType.ERROR,
                content={"error": str(e)},
                metadata={}
            )
