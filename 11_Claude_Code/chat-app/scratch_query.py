import asyncio
import os
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions

load_dotenv()

async def main():
    async for message in query(
        prompt="What does this project do? Answer in two sentences.",
        options=ClaudeAgentOptions(
            model=os.environ["ANTHROPIC_MODEL"],
            allowed_tools=["Read", "Glob", "Grep"],
            cwd=os.environ["TARGET_REPO_PATH"],
        ),
    ):
        print(type(message).__name__)
        if hasattr(message, "result"):
            print("\n" + message.result)

asyncio.run(main())
