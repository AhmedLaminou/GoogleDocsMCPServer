# Google Docs MCP Server — Status

## Completed

- Stdio-first Python MCP package with 50 tools
- One-command local browser OAuth
- Stable per-user token storage
- Safer public scope profile: `documents + drive.file`
- Optional explicit full-Drive self-hosted profile
- VS Code extension registration through `uvx`
- Optional FastAPI/SSE deployment mode
- Unit, stdio, SSE, package, and extension validation

## Maintainer action before public release

1. Create a Google OAuth **Desktop app** client.
2. Add its JSON as `google_docs_mcp_server/oauth_client.json`.
3. Test with approved OAuth test users.
4. Complete sensitive-scope OAuth verification.
5. Publish the Python package, then the VS Code extension.

End users should only install, run `google-docs-mcp-auth login`, and approve
access to their own Google account.

## Google API limitations

- Physical rendered page boundaries are unavailable; `read_page` uses explicit
  page breaks.
- Editor undo/revision restore is unavailable through the Docs API.
- Bookmark creation is unavailable; the tool creates a named range.
