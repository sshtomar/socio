# Coding Agent Service

LLM-powered coding assistant for Socio's marimo notebooks, inspired by the Jupybara project.

## Overview

The coding agent provides intelligent assistance for exploratory data analysis and impact evaluations, following three core design principles:

1. **Semantic Precision**: Statistically rigorous and technically accurate analysis
2. **Rhetorical Persuasion**: Clear, accessible explanations and narratives
3. **Pragmatic Relevance**: Executable, actionable code and insights

## Architecture

### Multi-Agent System (Phased Implementation)

**Phase 1 (Current)**: Simple prompt chaining with routing
- Query router (Haiku for fast classification)
- Quick executor (Sonnet for generation)
- Basic tool system for notebook interaction

**Phase 2**: Interactive planning
- Planner agent for complex EDA
- User approval workflow
- Step-by-step execution

**Phase 3**: Self-critique and refinement
- Quality evaluation against design dimensions
- Iterative refinement for complex analyses

**Phase 4**: Storytelling and insights
- Narrative generation
- Session-level insight tracking
- Report creation

### Query Routes

Queries are classified into five routes:

1. **quick_fix** (1-2s): Error debugging, syntax fixes
2. **simple_code** (2-3s): Basic operations, simple visualizations
3. **complex_eda** (5-15s): Multi-step analysis with planning
4. **explain** (2-3s): Interpretation and explanations
5. **storytelling** (5-8s): Narrative summaries and reports

## Setup

### Prerequisites

- Python 3.10+
- Anthropic API key

### Installation

```bash
cd services/coding-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Add your API key to .env
# ANTHROPIC_API_KEY=your_key_here
```

### Running the Service

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```bash
GET /health
```

### Quick Query (Non-Streaming)

```bash
POST /api/agent/quick
Content-Type: application/json

{
  "query": "Create a histogram of the age column",
  "context": {
    "notebook_id": "nb_123",
    "session_id": "session_456",
    "variables": {
      "df": "DataFrame"
    },
    "cell_count": 5
  }
}
```

### Streaming Query (WebSocket)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/agent/stream');

// Send query
ws.send(JSON.stringify({
  type: 'query',
  query: 'Analyze relationship between income and education',
  context: {
    notebook_id: 'nb_123',
    session_id: 'session_456',
    variables: { df: 'DataFrame' },
    cell_count: 5
  }
}));

// Receive messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message.type, message.content);
};
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
ruff check .
```

### Adding New Agents

1. Create agent class in `agents/` inheriting from `BaseAgent`
2. Implement system prompt in `prompts/system_prompts.py`
3. Add route handling in `core/orchestrator.py`
4. Update router classification if needed

## Tools

The agent has access to these notebook interaction tools:

- **inspect_dataframe**: Get schema and summary statistics
- **sample_data**: Retrieve sample rows (head/tail/random)
- **execute_cell**: Execute Python code in notebook
- **get_variables**: List available variables

## Configuration

Environment variables (see `.env.example`):

- `ANTHROPIC_API_KEY`: Required API key
- `DEFAULT_MODEL`: Model for generation (default: claude-sonnet-4-20250514)
- `ROUTER_MODEL`: Model for routing (default: claude-3-5-haiku-20241022)
- `ENABLE_SELF_CRITIQUE`: Enable Phase 3 critique (default: false)
- `MAX_TOKENS_PER_REQUEST`: Token limit (default: 8000)

## Cost Estimates

Based on Sonnet 4 pricing (~$3 input / ~$15 output per million tokens):

| Route | Tokens | Cost | Time |
|-------|--------|------|------|
| quick_fix | 1-2K | ~$0.01 | 1-2s |
| simple_code | 2-3K | ~$0.02 | 2-3s |
| complex_eda | 4-6K | ~$0.04 | 5-10s |
| explain | 2-3K | ~$0.02 | 2-3s |
| storytelling | 5-7K | ~$0.05 | 5-8s |

## Integration

This service integrates with:

- **Session Orchestrator**: For code execution in notebook runtimes
- **Workspace API**: For retrieving project metadata and storing insights
- **Notebook App**: Front-end client for user interactions

## Next Steps

- [ ] Implement session-orchestrator integration for code execution
- [ ] Add planner agent (Phase 2)
- [ ] Implement user approval workflow
- [ ] Add self-critique system (Phase 3)
- [ ] Create storyteller agent (Phase 4)
- [ ] Add insight tracking and retrieval
- [ ] Implement usage analytics and monitoring
