# Coding Agent Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Get Your API Key

Visit https://console.anthropic.com/settings/keys and create a new API key.

### 2. Set Up Environment

```bash
# Navigate to service directory
cd services/coding-agent

# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 4. Start the Service

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Test It Out

#### Test with cURL (Quick Query)

```bash
curl -X POST http://localhost:8000/api/agent/quick \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create a histogram",
    "context": {
      "notebook_id": "test_nb",
      "session_id": "test_session",
      "variables": {"df": "DataFrame"},
      "cell_count": 1
    }
  }'
```

#### Test with Python

```python
import asyncio
import websockets
import json

async def test_agent():
    uri = "ws://localhost:8000/api/agent/stream"

    async with websockets.connect(uri) as websocket:
        # Send query
        await websocket.send(json.dumps({
            "type": "query",
            "query": "Show first 5 rows of the dataframe",
            "context": {
                "notebook_id": "test_nb",
                "session_id": "test_session",
                "variables": {"df": "DataFrame"},
                "cell_count": 1
            }
        }))

        # Receive responses
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"{data['type']}: {data['content']}")

            if data['type'] == 'complete':
                break

asyncio.run(test_agent())
```

## 📊 What Just Happened?

1. **Router** classified your query (using Haiku - fast & cheap)
2. **Quick Executor** generated a response (using Sonnet 4 - high quality)
3. Response streamed back to you in real-time

## 🎯 Try Different Query Types

### Quick Fix (1-2s)
```json
{
  "query": "Fix this error: NameError: name 'pd' is not defined",
  "context": {
    "last_error": "NameError: name 'pd' is not defined",
    ...
  }
}
```

### Simple Code (2-3s)
```json
{
  "query": "Calculate mean and median of age column"
}
```

### Complex EDA (5-15s) - *Phase 2*
```json
{
  "query": "Analyze the relationship between income and education level"
}
```

### Explain (2-3s)
```json
{
  "query": "What does p-value mean in this context?"
}
```

## 🔍 Monitor Costs

Check the usage stats in each response:

```json
{
  "type": "usage",
  "content": {
    "input_tokens": 1500,
    "output_tokens": 500,
    "total_tokens": 2000,
    "estimated_cost_usd": 0.012
  }
}
```

## 🐛 Troubleshooting

### "API key not found"
- Make sure `.env` file exists in `services/coding-agent/`
- Check that `ANTHROPIC_API_KEY` is set correctly
- No spaces around the `=` sign

### "Connection refused"
- Service isn't running - run `python main.py`
- Check port 8000 isn't being used by another service

### "Import errors"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

## 📚 Next Steps

1. Read [README.md](./README.md) for full documentation
2. Check [architecture docs](../../docs/architecture-overview.md)
3. Explore the code in `agents/` and `prompts/`
4. Try implementing Phase 2 features (planning workflow)

## 💡 Tips

- Use `LOG_LEVEL=DEBUG` in `.env` to see detailed logs
- Router uses heuristics as fallback if API fails
- Tools are stubs - implement session-orchestrator integration for real execution
- Cost-optimize by using Haiku for simple queries in production

## 🤝 Need Help?

- Check service logs for errors
- Test with `/health` endpoint first
- Use heuristic router for offline testing
- See test examples in `tests/test_router.py`
