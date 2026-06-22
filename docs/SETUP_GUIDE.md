# Setup and Deployment Guide

## Google Cloud

1. Enable the Google Docs API and Google Drive API.
2. Configure an OAuth consent screen.
3. Create a **Web application** OAuth client.
4. Add `http://localhost:8000/oauth2callback` as a local redirect URI.
5. Add `https://your-domain.example/oauth2callback` for production.
6. Store the downloaded JSON as `credentials.json`, or set its full contents in `GOOGLE_CLIENT_SECRET_JSON`.

The requested scopes are full Docs and Drive access. Keep the server private.

## Local Run

```powershell
.\venv\Scripts\Activate.ps1
pip install -e .
google-docs-mcp-web
```

Open `http://localhost:8000/login` once. Successful consent creates `token.json`.

Check:

```text
GET http://localhost:8000/health
```

Expected after login:

```json
{"status":"ok","authenticated":true,"tool_count":50}
```

## MCP Connection

- SSE handshake: `GET /sse`
- Message channel: `POST /messages/`

If `MCP_API_KEY` is set, send:

```text
Authorization: Bearer <your-key>
```

## Production Configuration

Set all of these in the hosting platform:

```text
GOOGLE_CLIENT_SECRET_JSON=<full OAuth JSON>
GOOGLE_TOKEN_FILE=/persistent/path/token.json
PUBLIC_BASE_URL=https://your-domain.example
MCP_API_KEY=<long random secret>
MCP_SESSION_SECRET=<long random secret>
ALLOWED_HOSTS=your-domain.example
COOKIE_SECURE=true
```

The token path must survive restarts. Ephemeral filesystems will lose Google authorization.

Start command:

```text
python -m uvicorn google_docs_mcp_server.app:app --host 0.0.0.0 --port $PORT
```

## Docker

```powershell
docker build -t google-docs-mcp .
docker run --rm -p 8000:8000 --env-file .env google-docs-mcp
```

Mount persistent storage for `GOOGLE_TOKEN_FILE` in production.

## Verification

```powershell
python -m compileall -q google_docs_mcp_server
python -m unittest discover -s tests -v
python -c "import asyncio; from google_docs_mcp_server.server import mcp; print(len(asyncio.run(mcp.list_tools())))"
```

The last command must print `50`.
