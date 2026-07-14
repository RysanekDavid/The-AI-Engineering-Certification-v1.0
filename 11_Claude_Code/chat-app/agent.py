"""Agent seam.

This module is the single integration point for the Claude Agent SDK.
Everything else in the app talks only to `get_reply`.

Sessions map lives in memory; server restart = fresh conversations.
"""

import asyncio
import logging
import os
import sys

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    create_sdk_mcp_server,
    query,
    tool,
)

logger = logging.getLogger(__name__)


@tool(
    "count_lines",
    "Count lines of code in a single text file relative to cwd",
    {"file_path": str},
)
async def count_lines(args: dict) -> dict:
    cwd = os.path.normpath(os.environ["TARGET_REPO_PATH"])
    rel = args["file_path"].lstrip("/\\").replace("\\", "/")
    full = os.path.normpath(os.path.join(cwd, rel))
    # commonpath, not startswith: a sibling dir sharing the cwd string
    # prefix (repo_evil vs repo) must still be refused
    if os.path.commonpath([full, cwd]) != cwd:
        return {"content": [{"type": "text", "text": "Refused: path escapes target repo."}]}
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            n = sum(1 for _ in f)
        return {"content": [{"type": "text", "text": f"{rel}: {n} lines"}]}
    except FileNotFoundError:
        return {"content": [{"type": "text", "text": f"Not found: {rel}"}]}


_mcp_server = create_sdk_mcp_server(name="concierge", version="1.0.0", tools=[count_lines])

# conversation_id -> SDK session_id, updated after every successful turn
# (resume mints a new session_id each time)
_sessions: dict[str, str] = {}


async def get_reply(message: str, conversation_id: str) -> str:
    """Return the assistant reply for a user message.

    Runs an agent conversation against the repository at TARGET_REPO_PATH
    with read-only tools, resuming the SDK session tied to conversation_id
    when one exists. Always returns a string — errors are logged
    server-side and reported politely to the user.
    """
    cwd = os.environ["TARGET_REPO_PATH"]
    options = ClaudeAgentOptions(
        system_prompt=(
            f"You are a concierge for the repository at {cwd}. "
            "Answer concisely (max 3 short paragraphs). Cite file paths "
            "(relative to cwd) when you reference code. If uncertain, "
            "say so — do not invent."
        ),
        model=os.environ["ANTHROPIC_MODEL"],
        # read-only: no human at the gate server-side; custom MCP tools are
        # allowlisted as mcp__<server-key>__<tool-name>
        allowed_tools=["Read", "Glob", "Grep", "mcp__concierge__count_lines"],
        mcp_servers={"concierge": _mcp_server},
        cwd=cwd,
        max_turns=25,
        resume=_sessions.get(conversation_id),  # None on first call = fresh session
    )
    try:
        reply, session_id = await asyncio.to_thread(_run_query, message, options)
        if session_id:
            _sessions[conversation_id] = session_id
        return reply
    except Exception as exc:
        logger.exception("agent query failed")
        return f"Sorry — agent hit an error. Check server logs. ({type(exc).__name__})"


def _run_query(message: str, options: ClaudeAgentOptions) -> tuple[str, str | None]:
    """Run the SDK query on a private event loop in a worker thread.

    Uvicorn's --reload mode on Windows uses SelectorEventLoop, which cannot
    spawn subprocesses — and the SDK launches Claude Code as a subprocess.
    A dedicated ProactorEventLoop in this thread sidesteps that.
    """
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_collect_result(message, options))
    finally:
        loop.close()


async def _collect_result(
    message: str, options: ClaudeAgentOptions
) -> tuple[str, str | None]:
    """Return (reply, session_id) from the query stream.

    Only the "init" SystemMessage carries session_id — the SDK emits many
    SystemMessages of other subtypes.
    """
    new_session_id = None
    result = None
    # No early return: bailing out of the async for mid-stream makes the
    # SDK's generator raise "aclose(): asynchronous generator is already
    # running". ResultMessage is the last message, so draining is free.
    async for msg in query(prompt=message, options=options):
        if isinstance(msg, SystemMessage) and getattr(msg, "subtype", None) == "init":
            sid = getattr(msg, "data", {}).get("session_id")
            if sid:
                new_session_id = sid
        if isinstance(msg, ResultMessage) and msg.result is not None:
            result = msg.result
    if result is None:
        raise RuntimeError("stream ended without a ResultMessage.result")
    return result, new_session_id
