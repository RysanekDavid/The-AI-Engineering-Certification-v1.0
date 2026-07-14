<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 11: Claude Code & the Claude Agent SDK</h1>

| 📰 Session Sheet | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo | 📝 Homework | 📁 Feedback |
|:-----------------|:-------------|:----------|:----------|:------------|:------------|
| [Session 11: Claude Code & Claude Agent SDK ](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/11_Claude_Code) |[Recording!](https://us02web.zoom.us/rec/share/2I5HA6DwVFgmtyjPaq1SJDgkaVEuYZoWYyMCK8DOAZ99Zm6f7dTi0IGONXj6mRel.YHFzKF03mI5v6JAM) <br> passcode: `&Qhi!cf0`| [Session 11 Slides](https://canva.link/uw1cl42x84tm6zh) |You are here! <br><br> [Certification Challenge](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Certification%20Challenge) | [Optional Session 11 Assignment](https://forms.gle/sAyr5BgBLTfgJV8EA) <br><br>  [Cert Challenge Submission Form](https://forms.gle/xtM9F38nfRKcdjH97)| [Feedback 7/7](https://forms.gle/oDrguLDNvva65mtM8) |

## Useful Resources

**Claude Code**
- [Claude Code Documentation](https://code.claude.com/docs) — official docs: setup, workflows, settings
- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) — from install to first session
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) — Anthropic engineering guide

**Claude Agent SDK**
- [Agent SDK Overview](https://docs.anthropic.com/en/api/agent-sdk/overview) — what the SDK is and when to use it
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — Anthropic engineering deep dive

## Main Assignment

**Build a chat web app powered by the Claude Agent SDK** — and build it *with* Claude Code.

This session is markdown-only on purpose. There is no starter code and no notebook: every line of code in your final app will be written in collaboration with Claude Code. The session has one build arc across a single breakout room:

```text
you → Claude Code → chat app skeleton → wire in Agent SDK query()
      (FastAPI + chat UI, echo stub)      ├─ tools: Read / Glob / Grep
                                           └─ your custom tool
```

The finished product: a **codebase concierge** — a chat interface in the browser where an agent (with real tools) answers questions about any repository you point it at. In Session 10 you served models behind endpoints; today you serve an *agent* behind one.

Work through the three guides in order:

```text
01_Installing_Claude_Code.md   # install, authenticate, verify
02_Using_Claude_Code.md        # drive Claude Code; scaffold the chat app skeleton
03_Claude_Agent_SDK.md         # add the agent and connect it to your website
```

## Outline

### Breakout Room #1: Claude Code, the Agent SDK, and the Connection

- Task 1: Install Claude Code and authenticate ([guide](./01_Installing_Claude_Code.md))
- Task 2: Learn the loop — explore a repo you didn't write ([guide](./02_Using_Claude_Code.md))
- Task 3: Scaffold the chat app skeleton with Claude Code (plan → implement → verify)
- Task 4: Write the project's `CLAUDE.md`
- Question #1 and Question #2
- Task 5: Install the Agent SDK and run your first `query()` ([guide](./03_Claude_Agent_SDK.md))
- Task 6: Wire the agent into `/api/chat` — replace the echo stub
- Task 7: Conversation memory — resume sessions across messages
- Task 8: Give the agent a custom tool
- Question #3 and Question #4
- Activity #1: Level Up the Chat App

## Questions

### ❓ Question #1

While scaffolding in Task 3 you used **plan mode** before letting Claude Code write anything. Why does an agent that can execute shell commands need a permission system at all, and why is plan mode particularly valuable when starting a project from an empty directory?

#### ✅ Answer

An agent with shell access has arbitrary write access to your machine — a wrong tool call can install packages, rewrite files, or destroy work. The permission system inverts the default: nothing runs until you say yes. You stay the engineer of record.

Plan mode matters most on an empty directory because there is no code to constrain the agent's imagination — it can propose any framework, any layout, any set of dependencies. The moment BEFORE the first file is written is the cheap moment to steer. After scaffolding, rework is expensive; before it, changes cost one paragraph of feedback. Today I asked Claude Code to scaffold the chat app in plan mode, reviewed the layout, confirmed the `agent.get_reply()` swap seam was isolated, then approved implementation. Fifteen seconds of reading the plan saved an hour of undoing the wrong shape.

### ❓ Question #2

`CLAUDE.md` is loaded into context at the start of every session. What belongs in it — and what *doesn't*? How does this relate to what you learned about context management and memory in Session 3?

#### ✅ Answer

CLAUDE.md is loaded at the start of every session — every line costs context every single time. Belongs: things that are NOT discoverable by reading the code — the run command, the location of the swap seam (`agent.get_reply()`), conventions the code alone would not communicate (vanilla JS, isolated stub), non-obvious decisions. Does not belong: explanations of what FastAPI or uvicorn is, per-file prose, examples that duplicate what the code shows, stale in-progress notes.

Session 3 taught that context is finite and every token has a cost. There we solved it with summarization middleware — compress conversation history to keep the useful signal, drop the redundant volume. CLAUDE.md is the same problem at start-of-session instead of mid-session: keep the highest-signal facts, drop everything derivable from the code itself. My CLAUDE.md is 37 lines because the summarization instinct from Session 3 kicked in — anything longer would tax every future session, forever.

### ❓ Question #3

The Agent SDK gives you the same agent loop that powers Claude Code. Compare this to the agent loops you hand-built with LangGraph in Sessions 2–4: what does the SDK give you for free, and what control do you give up?

#### ✅ Answer

In LangGraph I built the loop myself: define state, wire model node → tool node → conditional edge back, decide when to stop, serialize messages, handle tool errors. The SDK collapses all of that into one call — `query()` runs the whole model → tool → observation cycle until the task is done. For free I got: the agent loop itself, a production tool suite (Read, Glob, Grep — file access I never had to implement), permission enforcement via `allowed_tools`, session persistence (`resume=session_id` replays the whole conversation — my Task 7 was a 10-line dict, not a checkpointer), cost tracking in `ResultMessage`, and `max_turns` as a built-in circuit breaker. Watching the message stream in `scratch_query.py` (SystemMessage init → AssistantMessage/tool cycles → ResultMessage) was literally watching my Session 2–4 graph, prebuilt.

What I gave up: the graph topology. In LangGraph every node and edge is mine — I can route between specialized sub-agents, inject validation nodes between steps, or short-circuit on custom conditions. With the SDK the loop is a black box: I choose the tools, the model, and the prompt, but not what happens between turns. I also inherited its runtime quirks — the SDK spawns Claude Code as a subprocess, which collided with uvicorn's Windows SelectorEventLoop and cost me a worker-thread workaround. Trade-off in one line: LangGraph is a framework for building agents; the SDK is a finished agent you configure. For a codebase concierge, configuration was all I needed.

### ❓ Question #4

Your chat app could have called a chat completions API directly, the way you did early in the course. What do you gain by routing every message through the Agent SDK's `query()` instead — and what new risks does an agent with tools introduce that a plain chat completion doesn't have? How did your tool allowlist and permission mode address them?

#### ✅ Answer

A chat completion can only talk about code from its training data or whatever I paste into the prompt. `query()` gives the model hands: it Reads, Globs and Greps the actual repository at answer time, so responses cite real files at their current state — my concierge answered dependency questions from the target repo's actual `package.json`, not from memory. It also grounds follow-ups ("what are *its* main dependencies?") in a persistent session instead of me re-sending history manually.

The same hands are the new risk. A plain completion's worst case is a wrong answer; an agent's worst case is a wrong *action* — editing files, running shell commands, exfiltrating data — triggered not just by the user but by anything the agent reads (prompt injection living inside the repo it browses). And there's a cost risk: a loop that never converges burns tokens forever. My mitigations, in layers: `allowed_tools=["Read", "Glob", "Grep"]` makes the agent read-only — no Write, no Bash, so even a fully hijacked agent can observe but not act (this matters doubly because a server has no human at the permission gate; the allowlist IS the permission mode). `max_turns=25` caps runaway loops. My custom `count_lines` tool validates paths with `commonpath` against `TARGET_REPO_PATH`, because the model could be talked into requesting `..\..\Windows\win.ini` — I tested exactly that and got the refusal. Rule of thumb: capabilities are granted per-deployment, not per-conversation — the server decides what the agent may ever do; the user only decides what it's asked to do.

## Activity 1: Level Up the Chat App

Extend your working chat app with **at least one** of the following (built with Claude Code, of course):

1. **Live progress streaming** — stream the agent's activity to the browser (e.g. via Server-Sent Events) so users see tool calls ("reading `app.py`…") while the agent works, instead of a spinner
2. **Multi-conversation support** — a sidebar of separate conversations, each mapped to its own SDK session
3. **A second custom tool** — something genuinely useful for your target repo (e.g. `git_log` for recent changes, or a test-runner summary tool)

Whichever you pick, demo it in your Loom video and explain the design decision in one paragraph.

## Advanced Activity: The Cat Shop Concierge

Connect your Session 8 cat shop MCP server to your chat app's agent via the SDK's `mcp_servers` option. Your chat app becomes a shopping concierge: users can browse the catalog, fill a cart, and check out — in natural language, through the UI you built, hitting the OAuth-protected server you wrote in Session 8.

Include your findings and a demo in your Loom video.

## Ship 🚢

The working chat app!

### Deliverables

- A short Loom showing:
  - Claude Code scaffolding or extending the app (plan → implement → verify — show the plan!); and
  - the chat app answering real questions about a repository, including at least one visible custom-tool use

## Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a chat app powered by the Claude Agent SDK — scaffolded entirely with Claude Code! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI agents. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#ClaudeCode #AgentSDK #AIAgents #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework (Optional For Extra Mark)

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Work through `01_Installing_Claude_Code.md`, `02_Using_Claude_Code.md`, and `03_Claude_Agent_SDK.md` in order.
3. Build your chat app in a new `chat-app/` folder inside this session directory (include its `CLAUDE.md` — we want to see it!).
4. Fill in your answers to Questions #1–#4 in this README.
5. Complete Activity #1 and record your Loom video.
6. Add, commit, and push your work to your origin repository. Remove `.env` files and API keys before committing.

When submitting your homework, provide the GitHub URL to your repo.
