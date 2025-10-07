"""
Query router for classifying user requests
"""

from anthropic import Anthropic
import logging
from typing import Optional

from schemas.internal import QueryRoute, NotebookContext
from prompts.router_prompts import ROUTER_SYSTEM_PROMPT, ROUTER_USER_TEMPLATE
from .config import get_settings

logger = logging.getLogger(__name__)


class QueryRouter:
    """Routes queries to appropriate handlers based on complexity and intent"""

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.client = Anthropic(api_key=api_key or settings.anthropic_api_key)
        self.model = settings.router_model

    async def classify(
        self,
        query: str,
        context: NotebookContext
    ) -> QueryRoute:
        """
        Classify a query into a route.

        Args:
            query: User's query text
            context: Notebook context

        Returns:
            QueryRoute enum value
        """
        try:
            # Format context for prompt
            variables_str = ", ".join(
                f"{k}:{v}" for k, v in context.variables.items()
            ) if context.variables else "None"

            user_message = ROUTER_USER_TEMPLATE.format(
                query=query,
                variables=variables_str,
                last_error=context.last_error or "None",
                cell_count=context.cell_count,
                is_empty=context.is_empty()
            )

            # Fast classification with Haiku
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                system=ROUTER_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )

            # Extract route from response
            route_text = response.content[0].text.strip().lower()

            # Map to enum
            route_mapping = {
                "quick_fix": QueryRoute.QUICK_FIX,
                "simple_code": QueryRoute.SIMPLE_CODE,
                "complex_eda": QueryRoute.COMPLEX_EDA,
                "explain": QueryRoute.EXPLAIN,
                "storytelling": QueryRoute.STORYTELLING,
            }

            route = route_mapping.get(route_text)

            if route is None:
                logger.warning(
                    f"Unknown route '{route_text}' from classifier, "
                    f"defaulting to simple_code"
                )
                route = QueryRoute.SIMPLE_CODE

            logger.info(f"Classified query as: {route.value}")
            return route

        except Exception as e:
            logger.error(f"Error classifying query: {e}", exc_info=True)
            # Default to simple_code on error
            return QueryRoute.SIMPLE_CODE

    def classify_heuristic(
        self,
        query: str,
        context: NotebookContext
    ) -> QueryRoute:
        """
        Fallback heuristic-based classification (no API call).

        This can be used for testing or as a backup if API fails.

        Args:
            query: User's query text
            context: Notebook context

        Returns:
            QueryRoute enum value
        """
        query_lower = query.lower()

        # Quick fix if there's an error
        if context.has_error():
            return QueryRoute.QUICK_FIX

        # Storytelling keywords
        if any(kw in query_lower for kw in ["summarize", "summary", "report", "tell me", "story"]):
            return QueryRoute.STORYTELLING

        # Explanation keywords
        if any(kw in query_lower for kw in ["explain", "what does", "what is", "interpret", "meaning"]):
            return QueryRoute.EXPLAIN

        # Complex EDA keywords
        if any(kw in query_lower for kw in [
            "analyze relationship",
            "compare",
            "correlation",
            "analysis",
            "investigate",
            "explore",
            "distribution",
            "test"
        ]):
            return QueryRoute.COMPLEX_EDA

        # Default to simple code
        return QueryRoute.SIMPLE_CODE
