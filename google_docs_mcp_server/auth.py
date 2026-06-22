"""Local OAuth and authenticated Google API clients."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DOCS_SCOPE = "https://www.googleapis.com/auth/documents"
DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"
FULL_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"

DEFAULT_SCOPES = [DOCS_SCOPE, DRIVE_FILE_SCOPE]
FULL_SCOPES = [DOCS_SCOPE, FULL_DRIVE_SCOPE]


def user_config_dir() -> Path:
    """Return a stable per-user directory without requiring platformdirs."""
    override = os.getenv("GOOGLE_DOCS_MCP_CONFIG_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if sys.platform == "win32":
        root = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        return root / "GoogleDocsMCP"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "GoogleDocsMCP"
    root = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "google-docs-mcp"


CONFIG_DIR = user_config_dir()
TOKEN_FILE = Path(
    os.getenv("GOOGLE_TOKEN_FILE", CONFIG_DIR / "token.json")
).expanduser().resolve()
USER_CREDENTIALS_FILE = Path(
    os.getenv("GOOGLE_CREDENTIALS_FILE", CONFIG_DIR / "oauth_client.json")
).expanduser().resolve()
PACKAGED_CREDENTIALS_FILE = Path(__file__).with_name("oauth_client.json")
LEGACY_CREDENTIALS_FILE = Path.cwd() / "credentials.json"
LEGACY_TOKEN_FILE = Path.cwd() / "token.json"


def scopes_for_profile(profile: str | None = None) -> list[str]:
    selected = (profile or os.getenv("GOOGLE_DOCS_MCP_SCOPE_PROFILE", "default")).lower()
    if selected in {"default", "safe", "public"}:
        return list(DEFAULT_SCOPES)
    if selected in {"full", "full-drive", "self-hosted"}:
        return list(FULL_SCOPES)
    raise ValueError("Scope profile must be 'default' or 'full'.")


SCOPES = scopes_for_profile()


def load_oauth_client_config() -> dict[str, Any]:
    """Load the publisher's desktop OAuth client or a self-hosted override."""
    credentials_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if credentials_json:
        try:
            return json.loads(credentials_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("GOOGLE_CLIENT_SECRET_JSON is not valid JSON.") from exc

    for path in (
        USER_CREDENTIALS_FILE,
        PACKAGED_CREDENTIALS_FILE,
        LEGACY_CREDENTIALS_FILE,
    ):
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))

    raise RuntimeError(
        "OAuth client configuration is missing. The package publisher must bundle "
        "google_docs_mcp_server/oauth_client.json, or a self-hoster can place a "
        f"Desktop OAuth JSON file at {USER_CREDENTIALS_FILE}."
    )


def load_desktop_oauth_client_config() -> dict[str, Any]:
    """Load and validate a Desktop OAuth client for local loopback auth."""
    client_config = load_oauth_client_config()
    if "installed" in client_config:
        return client_config
    raise RuntimeError(
        "Local package authentication requires a Google OAuth client of type "
        "'Desktop app'. The current credential is a Web application client. "
        "Create a Desktop app client and save it as "
        "google_docs_mcp_server/oauth_client.json."
    )


def save_credentials(credentials: Credentials) -> None:
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
    try:
        TOKEN_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def load_credentials(profile: str | None = None) -> Credentials | None:
    scopes = scopes_for_profile(profile)
    source = TOKEN_FILE
    if not source.exists() and LEGACY_TOKEN_FILE.exists():
        source = LEGACY_TOKEN_FILE
    if not source.exists():
        return None
    credentials = Credentials.from_authorized_user_file(str(source), scopes)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(credentials)
    elif credentials.valid and source != TOKEN_FILE:
        save_credentials(credentials)
    return credentials if credentials.valid else None


def authenticate(
    profile: str | None = None,
    *,
    force: bool = False,
    open_browser: bool = True,
) -> Credentials:
    """Authenticate this OS user through a browser and persist only their token locally."""
    if not force:
        existing = load_credentials(profile)
        if existing:
            return existing

    client_config = load_desktop_oauth_client_config()
    scopes = scopes_for_profile(profile)
    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
    credentials = flow.run_local_server(
        host="localhost",
        port=0,
        authorization_prompt_message=(
            "Open this URL to authorize Google Docs MCP:\n{url}\n"
        ),
        success_message=(
            "Google Docs MCP authorization succeeded. You can close this browser tab."
        ),
        open_browser=open_browser,
        access_type="offline",
        prompt="consent",
    )
    save_credentials(credentials)
    return credentials


def authentication_status() -> dict[str, Any]:
    credentials = load_credentials()
    try:
        load_desktop_oauth_client_config()
        desktop_client_available = True
    except RuntimeError:
        desktop_client_available = False
    return {
        "authenticated": credentials is not None,
        "token_file": str(TOKEN_FILE),
        "config_dir": str(CONFIG_DIR),
        "scope_profile": os.getenv("GOOGLE_DOCS_MCP_SCOPE_PROFILE", "default"),
        "scopes": scopes_for_profile(),
        "desktop_oauth_client_available": desktop_client_available,
    }


def logout() -> bool:
    if not TOKEN_FILE.exists():
        return False
    TOKEN_FILE.unlink()
    return True


def get_google_service(api_version: str = "v1"):
    """Build an authenticated Google Docs v1 or Drive v3 client."""
    credentials = load_credentials()
    if not credentials:
        raise RuntimeError(
            "Google Docs MCP is not authenticated. Run `google-docs-mcp-auth login` "
            "once, then restart the MCP client."
        )
    if api_version == "v1":
        return build("docs", "v1", credentials=credentials, cache_discovery=False)
    if api_version == "v3":
        return build("drive", "v3", credentials=credentials, cache_discovery=False)
    raise ValueError(f"Unsupported Google API version: {api_version}")
