"""Live stdio protocol smoke test for the installed console entry point."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    command = str(
        Path(__file__).resolve().parents[1]
        / "venv"
        / "Scripts"
        / "google-docs-mcp-server.exe"
    )
    parameters = StdioServerParameters(command=command)
    async with stdio_client(parameters) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.list_tools()
            print(f"stdio_tool_count: {len(result.tools)}")
            if len(result.tools) != 100:
                raise RuntimeError(f"Expected 100 tools, got {len(result.tools)}.")


if __name__ == "__main__":
    asyncio.run(main())
