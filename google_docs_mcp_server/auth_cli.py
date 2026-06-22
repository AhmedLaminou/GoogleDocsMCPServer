"""Command-line onboarding for local Google OAuth."""

from __future__ import annotations

import argparse
import json

from google_docs_mcp_server.auth import (
    TOKEN_FILE,
    authenticate,
    authentication_status,
    logout,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="google-docs-mcp-auth",
        description="Authenticate Google Docs MCP for the current OS user.",
    )
    subparsers = parser.add_subparsers(dest="command")

    login = subparsers.add_parser("login", help="Open Google OAuth in your browser.")
    login.add_argument(
        "--full-drive",
        action="store_true",
        help="Request restricted full-Drive access for a self-hosted client.",
    )
    login.add_argument("--force", action="store_true", help="Force fresh consent.")
    login.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the authorization URL instead of opening it.",
    )

    subparsers.add_parser("status", help="Show local authentication status.")
    subparsers.add_parser("logout", help="Delete this user's local OAuth token.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "login"

    if command == "login":
        profile = "full" if getattr(args, "full_drive", False) else "default"
        try:
            authenticate(
                profile,
                force=getattr(args, "force", False),
                open_browser=not getattr(args, "no_browser", False),
            )
        except RuntimeError as exc:
            parser.exit(2, f"Authentication setup error: {exc}\n")
        print(f"Authenticated successfully. Token stored at: {TOKEN_FILE}")
        return
    if command == "status":
        print(json.dumps(authentication_status(), indent=2))
        return
    if command == "logout":
        print("Local token removed." if logout() else "No local token was present.")
        return
    parser.error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
