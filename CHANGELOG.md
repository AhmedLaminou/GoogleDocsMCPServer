# Changelog

## 0.3.0

- Expanded the native tool set from 50 to 100 tools.
- Added Drive rename, restore, folders, permissions, revisions, and multi-format export.
- Added safer prepend, replace-content, and end-index document operations.
- Added links, richer text/paragraph formatting, headers, footers, sections, and page setup.
- Added table row/column insertion, deletion, merging, and unmerging.
- Added image inspection/replacement, named-range management, and full comment/reply editing.
- Added document structure and Google Docs tab tools.
- Fixed `move_to_folder` documentation to match its exclusive-move behavior.
- Added OAuth credential ignore safeguards and release CI.
- Changed the PyPI distribution name to `google-docs-mcp-server-ahmedlaminou`
  because the shorter name is owned by another publisher.

## 0.2.0

- Made stdio the primary package and extension transport.
- Added one-command local browser authentication.
- Moved tokens into stable per-user OS storage.
- Changed the public scope profile to `documents + drive.file`.
- Made restricted full-Drive access an explicit self-hosted profile.
- Retained FastAPI/SSE as an optional mode.

## 0.1.0

- Added 50 Google Docs and Drive MCP tools.
- Added installable Python package and stdio console entry point.
- Added hosted FastAPI/SSE entry point.
- Added Google OAuth setup and optional MCP bearer authentication.
- Added VS Code extension wrapper for GitHub Copilot Agent.
- Added tests, Docker support, MCP Registry metadata, and publishing documentation.
