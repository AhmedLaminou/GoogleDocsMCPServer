# Google Docs MCP Server

<!-- mcp-name: io.github.AhmedLaminou/google-docs-mcp-server -->

Google Docs MCP Server is a Python Model Context Protocol server exposing **50 tools** for Google Docs and Google Drive.

It supports two transports:

- **stdio** for local MCP clients, `uvx`, and the VS Code extension.
- **SSE over FastAPI** for hosted or remote deployments.

## Capabilities

- Create, copy, search, organize, share, unshare, trash, and export documents.
- Read full documents, ranges, headings, footnotes, links, tables, and explicit page-break sections.
- Insert text, lists, images, page breaks, footnotes, tables, and table-cell content.
- Apply text and paragraph formatting.
- Find and replace text, batch operations, clear ranges, rows, or documents.
- Create, reply to, list, and resolve Drive comments.

See [docs/TOOLS_REFERENCE.md](docs/TOOLS_REFERENCE.md) for all tools and signatures.

## Requirements

- Python 3.10+
- Google Docs API and Google Drive API enabled
- Google OAuth 2.0 Web Application credentials
- [`uv`](https://docs.astral.sh/uv/) when using the VS Code extension or `uvx`

## Python Package

Install in editable mode:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
```

This installs:

- `google-docs-mcp-server` — stdio MCP server
- `google-docs-mcp-web` — OAuth and hosted SSE server

## OAuth Setup

1. Save your Google OAuth web-client JSON as `credentials.json`.
2. Start the web server:

```powershell
google-docs-mcp-web
```

3. Open `http://localhost:8000/login`.
4. Complete consent. The server creates `token.json`.

Both secret files are ignored by Git.

## MCP Client Configuration

After the package is published to PyPI:

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "uvx",
      "args": ["google-docs-mcp-server"],
      "env": {
        "GOOGLE_TOKEN_FILE": "C:\\secure\\google-docs-mcp\\token.json"
      }
    }
  }
}
```

For a local editable installation:

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "C:\\path\\to\\GoogleDocsMCPServer\\venv\\Scripts\\google-docs-mcp-server.exe",
      "args": [],
      "env": {
        "GOOGLE_TOKEN_FILE": "C:\\path\\to\\GoogleDocsMCPServer\\token.json"
      }
    }
  }
}
```

## Hosted SSE Server

```powershell
google-docs-mcp-web
```

Endpoints:

- `GET /health`
- `GET /login`
- `GET /oauth2callback`
- `GET /sse`
- `POST /messages/`

For production, configure `PUBLIC_BASE_URL`, `MCP_API_KEY`, `MCP_SESSION_SECRET`, `ALLOWED_HOSTS`, `COOKIE_SECURE=true`, and persistent token storage.

## VS Code Extension

The `vscode-extension/` folder follows the same wrapper pattern as WindowsMCPServer and registers the PyPI package through `uvx`.

```powershell
cd vscode-extension
npm install
npm run compile
```

Open that folder in VS Code and press `F5` to launch an Extension Development Host.

## Development

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe -m compileall google_docs_mcp_server
.\venv\Scripts\python.exe -c "import asyncio; from google_docs_mcp_server.server import mcp; print(len(asyncio.run(mcp.list_tools())))"
```

The final command must print `50`.

## Google API Limitations

- Google does not expose rendered physical-page boundaries; `read_page` uses explicit page breaks.
- Google does not expose editor undo or revision restore; `undo_last_action` reports that limitation.
- Google does not expose bookmark creation; `insert_linked_bookmark` creates a named range.

## Publishing

See [docs/PUBLISHING.md](docs/PUBLISHING.md) for GitHub, PyPI, MCP Registry, and VS Code Marketplace steps.

## License

MIT. See [LICENSE](LICENSE).
