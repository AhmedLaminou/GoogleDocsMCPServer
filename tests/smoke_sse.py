"""Live SSE protocol smoke test. Requires the server on localhost:8000."""

from __future__ import annotations

import asyncio
import os

from mcp import ClientSession
from mcp.client.sse import sse_client


async def main() -> None:
    headers = None
    api_key = os.getenv("MCP_API_KEY")
    if api_key:
        headers = {"Authorization": f"Bearer {api_key}"}

    async with sse_client("http://127.0.0.1:8000/sse", headers=headers) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.list_tools()
            print(f"sse_tool_count: {len(result.tools)}")
            if len(result.tools) != 100:
                raise RuntimeError(f"Expected 100 tools, got {len(result.tools)}.")


if __name__ == "__main__":
    asyncio.run(main())
