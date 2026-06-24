# Google Docs MCP Server

<!-- mcp-name: io.github.AhmedLaminou/google-docs-mcp-server -->

An open-source, stdio-first MCP server exposing **100 Google Docs and Drive tools**.

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
uvx --from google-docs-mcp-server-ahmedlaminou google-docs-mcp-auth login
```

If the Google OAuth app is still in **Testing**, only Google accounts added as
test users in Google Cloud can complete this login. Production/public use
requires publishing the OAuth app and completing any required Google verification.

The browser consent flow stores the token in:

- Windows: `%APPDATA%\GoogleDocsMCP\token.json`
- macOS: `~/Library/Application Support/GoogleDocsMCP/token.json`
- Linux: `~/.config/google-docs-mcp/token.json`

Useful commands:

```powershell
google-docs-mcp-auth status
google-docs-mcp-auth logout
```

Optional reliability settings:

```powershell
$env:GOOGLE_DOCS_MCP_HTTP_TIMEOUT = "60"
$env:GOOGLE_DOCS_MCP_API_RETRIES = "2"
```

## MCP client

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "uvx",
      "args": [
        "--from",
        "google-docs-mcp-server-ahmedlaminou",
        "google-docs-mcp-server"
      ]
    }
  }
}
```

The VS Code extension registers this stdio server automatically.

## Permission profiles

The public/default profile requests:

- `documents` — read and edit Google Docs.
- `drive.file` — Drive operations for files created by or explicitly opened with the app.

This avoids the restricted full-Drive scope. The default profile can keep
working with Docs the app created in earlier sessions, but broad Drive
listing/search only sees files available to `drive.file`; it cannot enumerate
unrelated pre-existing Drive content.

Self-hosters and power users can intentionally opt into restricted full-Drive
access when they need broad discovery of existing Drive files:

```powershell
$env:GOOGLE_DOCS_MCP_SCOPE_PROFILE = "full"
google-docs-mcp-auth login --full-drive
```

Full Drive uses `https://www.googleapis.com/auth/drive`, which is a restricted
Google scope and may require a heavier OAuth verification process.

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

- Document creation, rename, copy, trash/restore, metadata, folders, permissions,
  revisions, and multi-format export.
- Reading text, ranges, headings, footnotes, links, tables, images, structure,
  named ranges, and document tabs.
- Text, lists, links, images, headers, footers, footnotes, sections, tables,
  table rows/columns, and tab insertion.
- Rich formatting, comments/replies, named ranges, page setup, and raw batch updates.

Image generation remains provider-neutral: an AI client may generate an image
with any capable model or service, then pass its public URL to
`insert_external_image` or `replace_image`.

See [docs/TOOLS_REFERENCE.md](docs/TOOLS_REFERENCE.md).

## Verification

```powershell
python -m unittest discover -s tests -v
python -m compileall google_docs_mcp_server
python tests/smoke_stdio.py
```

The stdio smoke test verifies registration. Live Google Docs/Drive behavior
requires a local authenticated account.

## License

MIT. See [LICENSE](LICENSE).
