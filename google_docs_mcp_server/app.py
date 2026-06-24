import os
import secrets
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from google_auth_oauthlib.flow import Flow
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from google_docs_mcp_server.auth import (
    LEGACY_TOKEN_FILE,
    SCOPES,
    TOKEN_FILE,
    load_oauth_client_config,
    save_credentials,
)
from google_docs_mcp_server import __version__
from google_docs_mcp_server.registry import register_all_tools
from google_docs_mcp_server.registry import TOOL_FUNCTIONS

# ==============================================================
# FAST-MCP & FASTAPI SERVER SETUP
# ==============================================================
# We must use FastAPI directly to handle SSE routes manually and OAuth routes.
app = FastAPI(title="Google Docs MCP Server", version=__version__)
mcp = FastMCP("GoogleDocsMCP")

class OptionalApiKeyMiddleware(BaseHTTPMiddleware):
    """Protect MCP transport routes when MCP_API_KEY is configured."""

    async def dispatch(self, request: Request, call_next):
        configured_key = os.getenv("MCP_API_KEY")
        protected = request.url.path == "/sse" or request.url.path.startswith("/messages/")
        if configured_key and protected:
            supplied = request.headers.get("authorization", "")
            expected = f"Bearer {configured_key}"
            if not secrets.compare_digest(supplied, expected):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or missing MCP API key."},
                )
        return await call_next(request)


app.add_middleware(OptionalApiKeyMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("MCP_SESSION_SECRET", secrets.token_urlsafe(32)),
    https_only=os.getenv("COOKIE_SECURE", "false").lower() == "true",
    same_site="lax",
)

allowed_hosts = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts or ["*"])


def _create_oauth_flow(redirect_uri: str, state: str | None = None) -> Flow:
    client_config = load_oauth_client_config()
    return Flow.from_client_config(
        client_config, scopes=SCOPES, redirect_uri=redirect_uri, state=state
    )


def _external_callback_url(request: Request) -> str:
    public_base_url = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    if public_base_url:
        return f"{public_base_url}/oauth2callback"
    return str(request.url_for("oauth2callback"))

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Google Docs MCP Server</title></head>
        <body style="font-family: Arial; padding: 50px;">
            <h1>Google Docs MCP Server is Live!</h1>
            <p>Connect your AI client to <code>/sse</code></p>
            <a href="/login" style="padding: 10px 20px; background: #4285F4; color: white; text-decoration: none; border-radius: 5px;">Login with Google</a>
            <hr>
            <p><b>Status:</b> Ready for Server-Sent Events mapping.</p>
        </body>
    </html>
    """

@app.get("/login")
async def login(request: Request):
    """Initiates the OAuth 2.0 Web flow"""
    try:
        flow = _create_oauth_flow(_external_callback_url(request))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    request.session["oauth_state"] = state
    return RedirectResponse(authorization_url)


@app.get("/oauth2callback")
async def oauth2callback(request: Request, state: str, code: str):
    """Receives the tokens back from Google"""
    expected_state = request.session.pop("oauth_state", None)
    if not expected_state or not secrets.compare_digest(state, expected_state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")
    try:
        flow = _create_oauth_flow(_external_callback_url(request), state=state)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    flow.fetch_token(authorization_response=str(request.url))
    save_credentials(flow.credentials)

    return "OAuth Successful! The MCP Server now has access to your Google Docs. You can close this window."

register_all_tools(mcp)

# ==============================================================
# SSE TRANSPORT (RENDER / VERCEL COMPATIBILITY BIND)
# ==============================================================
# Since FastMCP abstracts the SSE behind standard run commands,
# we need to bind the MCP router over the FastAPI instance explicitly.
# (FastMCP usually provides mcp.run("sse") which spins up its own starlette instance).
# Instead of manual binding, we will orchestrate it directly at entry.

_sse_transport = SseServerTransport("/messages/")


@app.get("/sse")
async def sse_endpoint(request: Request):
    """MCP SSE handshake endpoint."""
    async with _sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp._mcp_server.run(
            streams[0],
            streams[1],
            mcp._mcp_server.create_initialization_options(),
        )


app.mount("/messages/", _sse_transport.handle_post_message)

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "authenticated": TOKEN_FILE.exists() or LEGACY_TOKEN_FILE.exists(),
        "tool_count": len(TOOL_FUNCTIONS),
    }


if __name__ == "__main__":
    # Hosted entry point used by google-docs-mcp-web and deployment platforms.
    print("Starting Google Docs MCP Server locally on port 8000...")
    uvicorn.run(
        "google_docs_mcp_server.app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
