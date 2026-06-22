"""Backward-compatible web application module."""

from google_docs_mcp_server.app import app, mcp
from google_docs_mcp_server.web import main

__all__ = ["app", "mcp", "main"]


if __name__ == "__main__":
    main()
