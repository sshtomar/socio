"""
Tests for query router
"""

import pytest
from schemas.internal import NotebookContext, QueryRoute
from core.router import QueryRouter


class TestQueryRouter:
    """Test query classification"""

    def test_heuristic_quick_fix_with_error(self):
        """Test that queries with errors route to quick_fix"""
        router = QueryRouter()
        context = NotebookContext(
            notebook_id="test",
            session_id="test",
            last_error="NameError: name 'df' is not defined"
        )

        route = router.classify_heuristic("fix this error", context)
        assert route == QueryRoute.QUICK_FIX

    def test_heuristic_explain(self):
        """Test explanation routing"""
        router = QueryRouter()
        context = NotebookContext(
            notebook_id="test",
            session_id="test"
        )

        queries = [
            "explain what this means",
            "what does correlation mean",
            "interpret these results"
        ]

        for query in queries:
            route = router.classify_heuristic(query, context)
            assert route == QueryRoute.EXPLAIN

    def test_heuristic_storytelling(self):
        """Test storytelling routing"""
        router = QueryRouter()
        context = NotebookContext(
            notebook_id="test",
            session_id="test"
        )

        queries = [
            "summarize my analysis",
            "create a report",
            "tell me what I found"
        ]

        for query in queries:
            route = router.classify_heuristic(query, context)
            assert route == QueryRoute.STORYTELLING

    def test_heuristic_complex_eda(self):
        """Test complex EDA routing"""
        router = QueryRouter()
        context = NotebookContext(
            notebook_id="test",
            session_id="test",
            variables={"df": "DataFrame"}
        )

        queries = [
            "analyze the relationship between income and education",
            "compare treatment and control groups",
            "test for correlation"
        ]

        for query in queries:
            route = router.classify_heuristic(query, context)
            assert route == QueryRoute.COMPLEX_EDA

    def test_heuristic_simple_code(self):
        """Test simple code routing (default)"""
        router = QueryRouter()
        context = NotebookContext(
            notebook_id="test",
            session_id="test",
            variables={"df": "DataFrame"}
        )

        queries = [
            "show first 5 rows",
            "filter where age > 30",
            "create a histogram"
        ]

        for query in queries:
            route = router.classify_heuristic(query, context)
            assert route == QueryRoute.SIMPLE_CODE
