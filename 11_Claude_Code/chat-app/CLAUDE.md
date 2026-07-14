# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
uv sync                                # install deps (Python 3.12+, managed by uv)
uv run uvicorn main:app --reload       # run dev server at http://localhost:8000
```

Test the chat endpoint (curl may be blocked by permissions; python urllib works):

```sh
uv run python -c "import json,urllib.request; req=urllib.request.Request('http://localhost:8000/api/chat', data=json.dumps({'message':'hello','conversation_id':'test'}).encode(), headers={'Content-Type':'application/json'}); print(urllib.request.urlopen(req).read().decode())"
```

No test suite or linter configured yet.

## Architecture

The one thing to know: **all chat logic lives in a single swappable function** —
`agent.get_reply(message, conversation_id) -> str` in `agent.py`, backed by the
Claude Agent SDK. `POST /api/chat` in `main.py` is the only caller.

Tools the agent has:
- Built-in: `Read`, `Glob`, `Grep` (read-only file access to TARGET_REPO_PATH)
- Custom (in-process MCP, defined in `agent.py`):
  - `count_lines(file_path)` — line count for a single file (path-traversal guarded)
  - `query_recent_prices(currency_name, limit)` — read-only SQL over
    `TARGET_REPO_PATH/data/poe2flip.db` `price_snapshots` table; parameterized

- `main.py` — FastAPI app; `load_dotenv()` must run before anything reads env vars
- `static/` — plain HTML/CSS/JS frontend, no framework, no build step
- `conversation_id` is generated per page load in `app.js`; agent.py maps it to
  SDK session ids in an in-memory dict — server restart = fresh conversations
- Windows quirk: the SDK spawns Claude Code as a subprocess, which uvicorn
  `--reload`'s SelectorEventLoop can't do — agent.py runs queries on a private
  ProactorEventLoop in a worker thread. Don't "simplify" that away.
- uvicorn `--reload` on Windows can hang mid-reload with the old worker still
  serving — after editing agent.py, verify the log shows a completed restart

## Conventions

- Frontend stays vanilla JS — do not introduce a framework or build step
- Keep the agent stub isolated: no Anthropic/SDK imports outside `agent.py`
- Env config via `.env` (gitignored); update `.env.example` when adding vars
