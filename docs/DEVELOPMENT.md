# Development Guide

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
```

## Run

Authenticate:

```powershell
google-docs-mcp-auth login
```

Stdio:

```powershell
google-docs-mcp-server
```

Optional SSE:

```powershell
google-docs-mcp-web
```

## Verify

```powershell
python -m compileall google_docs_mcp_server
python -m unittest discover -s tests -v
python -c "import asyncio; from google_docs_mcp_server.server import mcp; print(len(asyncio.run(mcp.list_tools())))"
```

Expected tool count: `50`.

Extension:

```powershell
cd vscode-extension
npm install
npm run compile
```

## Add a Tool

1. Add the function to the appropriate module in `google_docs_mcp_server/tools/`.
2. Register it in `google_docs_mcp_server/registry.py`.
3. Add mocked behavior tests.
4. Update `docs/TOOLS_REFERENCE.md`.
5. Keep the registry count and package/extension descriptions synchronized.
