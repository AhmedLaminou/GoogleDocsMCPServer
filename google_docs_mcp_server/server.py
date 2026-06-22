"""Stdio entry point used by MCP clients, uvx, and the VS Code extension."""

from mcp.server.fastmcp import FastMCP

from google_docs_mcp_server.registry import register_all_tools

mcp = FastMCP("Google Docs MCP")
register_all_tools(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
