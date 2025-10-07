"""
Simple test client to verify the coding agent service
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_query(query_text, context=None):
    """Test a query and print results"""
    if context is None:
        context = {
            "notebook_id": "test_nb",
            "session_id": "test_session",
            "variables": {"df": "DataFrame"},
            "cell_count": 1
        }

    response = requests.post(
        f"{BASE_URL}/api/agent/quick",
        json={
            "query": query_text,
            "context": context
        }
    )

    data = response.json()

    print(f"\n{'='*80}")
    print(f"Query: {query_text}")
    print(f"{'='*80}")

    for msg in data["messages"]:
        if msg["type"] == "thinking":
            print(f"\nResponse:\n{msg['content'][:500]}...")  # First 500 chars
        elif msg["type"] == "usage":
            usage = msg["content"]
            print(f"\nUsage:")
            print(f"  Tokens: {usage['total_tokens']} ({usage['input_tokens']} in + {usage['output_tokens']} out)")
            print(f"  Cost: ${usage['estimated_cost_usd']:.6f}")

    return data


if __name__ == "__main__":
    # Test 1: Simple code generation
    print("\n🧪 Test 1: Simple Code Generation")
    test_query("Show first 5 rows of df")

    # Test 2: With error context (should route to quick_fix)
    print("\n\n🧪 Test 2: Error Fix")
    test_query(
        "Fix this error",
        context={
            "notebook_id": "test_nb",
            "session_id": "test_session",
            "variables": {},
            "last_error": "NameError: name 'pd' is not defined",
            "cell_count": 1
        }
    )

    # Test 3: Explanation request
    print("\n\n🧪 Test 3: Explanation")
    test_query("What does p-value mean?")

    # Test 4: Complex analysis
    print("\n\n🧪 Test 4: Complex Analysis")
    test_query("Analyze the relationship between income and education")

    print("\n\n✅ All tests completed!")
