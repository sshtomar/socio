# Session Management & Stateful Conversations

## Overview

The coding agent now maintains **stateful conversations** across multiple turns, allowing continuous discussion while preserving context and notebook state.

---

## ✅ What's Now Supported

### 1. **Conversation History**
- Each session maintains full conversation history
- User queries and assistant responses are tracked
- History is passed to agent for context-aware responses

### 2. **Notebook State Tracking**
- Variables in the notebook are tracked per session
- Agent aware of what data structures exist
- State updates automatically with each query

### 3. **Multi-Turn Continuity**
- Agent can reference previous turns
- No need to repeat context
- Natural conversation flow

---

## How It Works

### Architecture

```
┌──────────────────────────────────────────────┐
│         Session Manager                      │
│  (In-memory storage of conversations)        │
└─────────────┬────────────────────────────────┘
              │
              ├─> SessionState (per session_id)
              │   ├─> conversation_history[]
              │   ├─> notebook_variables{}
              │   └─> last_activity
              │
              ↓
┌──────────────────────────────────────────────┐
│      Agent Orchestrator                      │
│                                              │
│  1. Get/create session                       │
│  2. Add user query to history                │
│  3. Update notebook variables                │
│  4. Process query with full context          │
│  5. Save assistant response                  │
└──────────────────────────────────────────────┘
```

### Data Flow

```
Turn 1:
User: "Load data.csv"
├─> Saved to history
├─> Agent generates response
└─> Response saved to history

Turn 2:
User: "What columns are there?"
├─> Retrieved: Turn 1 context
├─> Agent knows data was loaded
└─> Provides column information

Turn 3:
User: "Create a histogram"
├─> Retrieved: Turn 1 + Turn 2 context
├─> Agent knows dataset structure
└─> Generates appropriate visualization
```

---

## API Usage

### Making a Query (Automatically Stateful)

```bash
curl -X POST http://localhost:8000/api/agent/quick \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What variables are available?",
    "context": {
      "notebook_id": "nb_123",
      "session_id": "session_456",  # Same session_id = continued conversation
      "variables": {"df": "DataFrame"},
      "cell_count": 5
    }
  }'
```

### View Session History

```bash
# Get last 20 turns
GET /api/sessions/{session_id}/history

# Get last N turns
GET /api/sessions/{session_id}/history?max_turns=10
```

**Response:**
```json
{
  "session_id": "session_456",
  "turn_count": 6,
  "history": [
    {"role": "user", "content": "Load data.csv"},
    {"role": "assistant", "content": "```python\nimport pandas as pd..."},
    {"role": "user", "content": "What columns are there?"},
    {"role": "assistant", "content": "The dataset has..."},
    ...
  ]
}
```

### Get Session Info

```bash
GET /api/sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "session_456",
  "notebook_id": "nb_123",
  "turn_count": 6,
  "last_activity": "2025-10-07T13:13:45",
  "variables": ["df", "age", "income"]
}
```

### Clear Session

```bash
DELETE /api/sessions/{session_id}
```

---

## Example: Multi-Turn Conversation

```python
import requests

BASE_URL = "http://localhost:8000"
SESSION_ID = "my_analysis_001"

def query(text, variables=None):
    return requests.post(
        f"{BASE_URL}/api/agent/quick",
        json={
            "query": text,
            "context": {
                "notebook_id": "nb_123",
                "session_id": SESSION_ID,
                "variables": variables or {},
                "cell_count": 1
            }
        }
    ).json()

# Turn 1: Load data
result1 = query("Load data.csv")
# Agent: "I've loaded the data..."

# Turn 2: Ask about data (agent remembers Turn 1)
result2 = query("How many rows?", {"df": "DataFrame"})
# Agent: "The dataset has X rows" (knows we're talking about df from Turn 1)

# Turn 3: Analysis (agent has full context)
result3 = query("Show correlation between age and income", {"df": "DataFrame"})
# Agent: Generates correlation analysis (understands the dataset)

# View history
history = requests.get(f"{BASE_URL}/api/sessions/{SESSION_ID}/history").json()
print(f"Conversation has {history['turn_count']} turns")
```

---

## Session Lifecycle

### Creation
- Sessions created automatically on first query with a `session_id`
- No explicit initialization needed

### Storage
- **In-memory**: Sessions stored in RAM (fast, but not persistent across restarts)
- **TODO**: Add persistent storage (Redis/Database) for production

### Cleanup
- Automatic: Sessions older than 24 hours are cleaned up
- Manual: Use `DELETE /api/sessions/{session_id}` to clear

### Limits
- Default: 1000 concurrent sessions
- Configurable via `SessionManager(max_sessions=N)`

---

## What's Still Needed for Full Statefulness

### ❌ Currently Missing

1. **Real Notebook Integration**
   - Tools return stub data
   - Need session-orchestrator connection
   - Can't actually execute code in notebooks yet

2. **Variable State Sync**
   - Agent doesn't fetch actual variable values
   - Relies on client to send variables in context
   - Need real-time sync with notebook runtime

3. **Persistent Storage**
   - Sessions lost on service restart
   - Should use Redis or database for persistence

### ✅ Already Working

1. **Conversation History** ✓
2. **Session Management** ✓
3. **Context Awareness** ✓
4. **Multi-Turn Logic** ✓
5. **Session APIs** ✓

---

## Implementation Roadmap

### Phase 1.5 (Current)
- ✅ In-memory session storage
- ✅ Conversation history tracking
- ✅ Session API endpoints
- ✅ Multi-turn conversations

### Phase 2 (Next)
- [ ] Session-orchestrator integration
- [ ] Real code execution in notebooks
- [ ] Auto-sync notebook variables
- [ ] Persistent session storage (Redis)

### Phase 3 (Future)
- [ ] Session replay/undo
- [ ] Branch conversations
- [ ] Export conversation history
- [ ] Session sharing between users

---

## Configuration

```python
# Environment variables
SESSION_MAX_AGE_HOURS=24  # Auto-cleanup threshold
SESSION_MAX_CONCURRENT=1000  # Max active sessions
SESSION_HISTORY_LIMIT=100  # Max turns per session
```

---

## Monitoring

### View Active Sessions

```bash
# Get session info
GET /api/sessions/{session_id}

# Response includes:
# - turn_count: Number of conversation turns
# - last_activity: Timestamp of last interaction
# - variables: List of tracked notebook variables
```

### Debug Session State

```python
# In Python client
import requests

session_info = requests.get(
    f"http://localhost:8000/api/sessions/{session_id}"
).json()

print(f"Session has {session_info['turn_count']} turns")
print(f"Variables: {session_info['variables']}")
print(f"Last active: {session_info['last_activity']}")
```

---

## Best Practices

### 1. **Use Consistent session_id**
```python
# Good: Same session_id for related queries
SESSION_ID = f"user_{user_id}_notebook_{notebook_id}"

# Bad: Random session_id each time
SESSION_ID = f"session_{random()}"  # Don't do this!
```

### 2. **Update Variables in Context**
```python
# After executing code, update variables
context = {
    "session_id": SESSION_ID,
    "notebook_id": notebook_id,
    "variables": get_current_variables(),  # Keep updated!
    ...
}
```

### 3. **Clear Old Sessions**
```python
# When user closes notebook
requests.delete(f"{BASE_URL}/api/sessions/{session_id}")
```

### 4. **Handle History Limits**
```python
# For very long conversations
history = requests.get(
    f"{BASE_URL}/api/sessions/{session_id}/history?max_turns=50"
).json()  # Only get recent context
```

---

## Testing

### Test Multi-Turn Conversation

```bash
cd services/coding-agent
source venv/bin/activate
python test_session.py
```

### Verify Session Persistence

```python
# Send multiple queries with same session_id
# Check history grows
# Verify context is maintained
```

---

## Summary

✅ **Enabled**: Multi-turn stateful conversations
✅ **Working**: Session management, history tracking, context awareness
✅ **API**: Full CRUD operations on sessions
⚠️ **Needs**: Real notebook integration for full state sync

The foundation is in place - sessions work end-to-end with conversation continuity. The next step is connecting to actual notebook runtimes via session-orchestrator!
