# chat-app

Codebase concierge: chat web app whose backend is a Claude Agent SDK loop with
read-only tools pointed at a target repository. FastAPI backend, plain
HTML/CSS/JS frontend, one swappable agent function.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Anthropic API key (`ANTHROPIC_API_KEY`)
- A local target repository the agent will answer questions about
  (`TARGET_REPO_PATH`). The `query_recent_prices` custom tool additionally
  expects `<TARGET_REPO_PATH>/data/poe2flip.db` with a `price_snapshots`
  table (columns: `id`, `fetched_at`, `item_name`, `chaos_equiv`, `volume`).
  If the DB is absent, the tool returns a polite "not found" message — the
  agent still works, that tool just becomes unavailable in practice.

## Setup

```sh
uv sync
cp .env.example .env   # then fill in real values
```

## Run

```sh
uv run uvicorn main:app --reload
```

Open http://localhost:8000

## API

```
POST /api/chat
{"message": "What does this repo do?", "conversation_id": "abc"}
→ {"reply": "<agent answer, may cite file paths>"}
```

`conversation_id` maps to an SDK session so follow-ups keep context; refresh =
new conversation. Server restart drops all session state (in-memory map).

## Structure

```
static/index.html   chat UI
static/style.css    styling
static/app.js       fetch + render logic; conversation_id per page load
main.py             FastAPI app, dotenv load, routes
agent.py            get_reply() — the swap seam; SDK query() + custom tools
scratch_query.py    standalone SDK smoke test (Task 5 reference)
```

## Agent config (agent.py)

- Model from `ANTHROPIC_MODEL` env var
- Working dir from `TARGET_REPO_PATH`
- Allowed tools: `Read`, `Glob`, `Grep`, `mcp__concierge__count_lines`,
  `mcp__concierge__query_recent_prices`
- `max_turns=25` circuit breaker
- Errors surface as polite chat replies (never a 500); traceback goes to logs

## Windows note

The SDK spawns Claude Code as a subprocess, which uvicorn `--reload`'s
`SelectorEventLoop` cannot do. `agent.py` runs the SDK on a private
`ProactorEventLoop` in a worker thread — do not simplify that away.
