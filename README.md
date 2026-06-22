# Google Docs MCP Server

<!-- mcp-name: io.github.AhmedLaminou/google-docs-mcp-server -->

An open-source, stdio-first MCP server exposing **50 Google Docs and Drive tools**.

## User experience

End users do not need their own Google Cloud project. The published package uses this project's public Desktop OAuth client identity. Each user signs into their own Google account and stores a separate token only on their own machine.

```text
User prompt → AI client → local stdio MCP server
            → user's local OAuth token → user's Google Docs
```

The publisher does not receive user tokens or document content in local stdio mode.

## Install and authenticate

After publication:

```powershell
uvx --from google-docs-mcp-server google-docs-mcp-auth login
```

The browser consent flow stores the token in:

- Windows: `%APPDATA%\GoogleDocsMCP\token.json`
- macOS: `~/Library/Application Support/GoogleDocsMCP/token.json`
- Linux: `~/.config/google-docs-mcp/token.json`

Useful commands:

```powershell
google-docs-mcp-auth status
google-docs-mcp-auth logout
```

## MCP client

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "uvx",
      "args": ["google-docs-mcp-server"]
    }
  }
}
```

The VS Code extension registers this stdio server automatically.

## Permission profiles

The public/default profile requests:

- `documents` — read and edit Google Docs.
- `drive.file` — Drive operations for files created by or explicitly opened with the app.

This avoids the restricted full-Drive scope. Broad Drive listing/search and permission operations therefore only see files available to `drive.file`.

Self-hosters can intentionally opt into restricted full-Drive access:

```powershell
$env:GOOGLE_DOCS_MCP_SCOPE_PROFILE = "full"
google-docs-mcp-auth login --full-drive
```

## Developer setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
google-docs-mcp-auth login
google-docs-mcp-server
```

Before a public release, the maintainer must create a Google OAuth client of type **Desktop app** and save its downloaded JSON as:

```text
google_docs_mcp_server/oauth_client.json
```

Desktop OAuth clients are public clients: their client identifier and nominal client secret cannot be kept confidential in a distributed/open-source desktop application. User refresh tokens remain private on each user's machine.

Self-hosters can instead put their own OAuth JSON at `%APPDATA%\GoogleDocsMCP\oauth_client.json` or set `GOOGLE_CREDENTIALS_FILE`.

## Optional hosted mode

FastAPI/SSE remains available:

```powershell
google-docs-mcp-web
```

It is not the default public architecture because true multi-user hosting requires per-user sessions and secure server-side token storage.

## Capabilities

- Document creation, copying, deletion, metadata, organization, sharing, and PDF export.
- Reading text, ranges, headings, footnotes, links, and tables.
- Text, list, image, footnote, table, and table-cell insertion.
- Formatting, comments, replies, named ranges, and batch updates.

See [docs/TOOLS_REFERENCE.md](docs/TOOLS_REFERENCE.md).

## Verification

```powershell
python -m unittest discover -s tests -v
python -m compileall google_docs_mcp_server
python tests/smoke_stdio.py
```

## License

MIT. See [LICENSE](LICENSE).
