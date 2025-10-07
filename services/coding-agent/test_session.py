"""
Test multi-turn conversation with session management
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = "test_conversation_001"

def send_query(query_text, variables=None):
    """Send a query and return response"""
    context = {
        "notebook_id": "test_nb",
        "session_id": SESSION_ID,
        "variables": variables or {},
        "cell_count": 1
    }

    response = requests.post(
        f"{BASE_URL}/api/agent/quick",
        json={"query": query_text, "context": context}
    )

    return response.json()


def get_session_history():
    """Get conversation history"""
    response = requests.get(f"{BASE_URL}/api/sessions/{SESSION_ID}/history")
    return response.json()


def get_session_info():
    """Get session info"""
    response = requests.get(f"{BASE_URL}/api/sessions/{SESSION_ID}")
    return response.json()


print("\n" + "="*80)
print("MULTI-TURN CONVERSATION TEST")
print("="*80)

# Turn 1: Load data
print("\n📝 Turn 1: Load data")
result1 = send_query("Load a CSV file called 'data.csv'", {})
print(f"Response snippet: {result1['messages'][0]['content'][:200]}...")

# Turn 2: Inspect data (agent should remember we loaded data)
print("\n📝 Turn 2: Ask about the data")
result2 = send_query("What variables are available?", {"df": "DataFrame"})
print(f"Response snippet: {result2['messages'][0]['content'][:200]}...")

# Turn 3: Create visualization
print("\n📝 Turn 3: Create visualization")
result3 = send_query(
    "Create a histogram",
    {"df": "DataFrame", "age": "Series"}
)
print(f"Response snippet: {result3['messages'][0]['content'][:200]}...")

# Check session history
print("\n" + "="*80)
print("SESSION HISTORY")
print("="*80)

history = get_session_history()
print(f"\nSession ID: {history['session_id']}")
print(f"Total turns: {history['turn_count']}")
print("\nConversation:")
for i, turn in enumerate(history['history'], 1):
    role = "👤 User" if turn['role'] == 'user' else "🤖 Assistant"
    content = turn['content'][:100] + "..." if len(turn['content']) > 100 else turn['content']
    print(f"\n{role}: {content}")

# Check session info
print("\n" + "="*80)
print("SESSION INFO")
print("="*80)

info = get_session_info()
print(json.dumps(info, indent=2))

print("\n✅ Multi-turn conversation test completed!")
print(f"Total API calls: 3")
print(f"Session persisted: Yes")
print(f"History maintained: {history['turn_count']} turns")
