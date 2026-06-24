# Setup Guide

## End users

End users need Python/`uv` and a Google account, not a Google Cloud project.

```powershell
uvx --from google-docs-mcp-server-ahmedlaminou google-docs-mcp-auth login
```

If the OAuth app is in Testing, the Google account must be added as a test user
by the maintainer.

After consent, an MCP client launches:

```powershell
uvx --from google-docs-mcp-server-ahmedlaminou google-docs-mcp-server
```

## Maintainer: Google Cloud

1. Select the Google Docs MCP Cloud project.
2. Enable Google Docs API and Google Drive API.
3. Configure Google Auth Platform branding, audience, and data access.
4. Create a client under **Clients → Create client → Desktop app**.
5. Download its JSON as `google_docs_mcp_server/oauth_client.json` for local
   testing and release builds. This exact path is ignored by Git.
6. Never package or commit a user `token.json`.

Configure the public/default scopes:

```text
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/drive.file
```

The Docs scope is sensitive and normally requires OAuth verification for a polished public release. `drive.file` is Google's recommended non-sensitive per-file Drive scope.

Avoid public use of `https://www.googleapis.com/auth/drive` unless you accept restricted-scope verification and possible security-assessment requirements.

## Testing

While the OAuth app is in Testing, add accounts under:

```text
Google Auth Platform → Audience → Test users
```

Only listed accounts can consent.
Testing-mode grants expire after seven days, including refresh tokens obtained
for offline access.

## Production and verification

Publishing removes the test-user-only restriction, but it does not replace sensitive-scope verification. Prepare branding, support contacts, homepage/privacy links, scope justification, and an OAuth demonstration video.

## Self-hosting

Override the public client:

```text
GOOGLE_CREDENTIALS_FILE=C:\secure\oauth_client.json
```

Opt into full Drive:

```powershell
$env:GOOGLE_DOCS_MCP_SCOPE_PROFILE = "full"
google-docs-mcp-auth login --full-drive --force
```

Full Drive is useful for broad discovery of existing Drive files, but it uses
the restricted `https://www.googleapis.com/auth/drive` scope. Keep the default
`drive.file` profile for public release unless restricted-scope verification is
intentional.

## Optional SSE

```powershell
google-docs-mcp-web
```

SSE remains available for controlled deployments. A public multi-user hosted service requires a per-user token database and session architecture.
