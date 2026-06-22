"""OAuth configuration and authenticated Google API clients."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = Path(
    os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
).expanduser().resolve()
TOKEN_FILE = Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json")).expanduser().resolve()


def load_oauth_client_config() -> dict[str, Any]:
    """Load OAuth client settings from an environment secret or JSON file."""
    credentials_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
    if credentials_json:
        try:
            return json.loads(credentials_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("GOOGLE_CLIENT_SECRET_JSON is not valid JSON.") from exc

    if not CREDENTIALS_FILE.exists():
        raise RuntimeError(
            "OAuth credentials are missing. Set GOOGLE_CLIENT_SECRET_JSON "
            "or provide GOOGLE_CREDENTIALS_FILE."
        )
    return json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))


def get_google_service(api_version: str = "v1"):
    """Build an authenticated Google Docs v1 or Drive v3 client."""
    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "Not authenticated. Run google-docs-mcp-web and visit /login."
        )
    credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if api_version == "v1":
        return build("docs", "v1", credentials=credentials, cache_discovery=False)
    if api_version == "v3":
        return build("drive", "v3", credentials=credentials, cache_discovery=False)
    raise ValueError(f"Unsupported Google API version: {api_version}")
