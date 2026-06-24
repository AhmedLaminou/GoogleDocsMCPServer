# Privacy Policy

Last updated: 2026-06-24

Google Docs MCP Server is an open-source local MCP server for automating Google
Docs and Google Drive actions from compatible AI clients.

## Data the App Accesses

When you authenticate with Google, the app may request access to:

- Google Docs content, so it can create, read, edit, and format documents at
  your request.
- Google Drive file access through `drive.file`, so it can create, move, rename,
  export, share, trash, restore, and inspect files that are available to the app.
- Optional full-Drive access only if you explicitly use the `--full-drive`
  profile.

The exact access depends on the OAuth scopes you approve during sign-in.

## How Data Is Used

Google user data is used only to provide the MCP tools you invoke, such as
creating documents, editing text, exporting files, listing permitted files,
managing folders, comments, revisions, permissions, images, tables, and document
tabs.

The app does not use Google user data for advertising, profiling, or selling
data.

## Local Storage

In the default stdio setup, the MCP server runs on your own machine. Your Google
OAuth token is stored locally in your operating-system user configuration
directory:

- Windows: `%APPDATA%\GoogleDocsMCP\token.json`
- macOS: `~/Library/Application Support/GoogleDocsMCP/token.json`
- Linux: `~/.config/google-docs-mcp/token.json`

The publisher does not receive your OAuth token or document contents when you
use the local stdio server.

## Sharing and Disclosure

The project does not operate a public backend service for collecting or storing
your Google Docs data. Data may still be processed by:

- Google APIs, according to Google's own terms and privacy policies.
- Your chosen AI client, according to that client's policies.
- Any self-hosted server or hosted deployment you configure.

Do not use a hosted deployment unless you trust its operator.

## Optional Hosted Mode

The repository includes an optional FastAPI/SSE mode for controlled deployments.
That mode is not the default public architecture. Anyone operating a hosted
deployment is responsible for secure per-user sessions, token storage, access
control, and compliance obligations.

## Data Retention and Deletion

The local server keeps your OAuth token until you remove it. You can delete the
local token with:

```powershell
google-docs-mcp-auth logout
```

You can also revoke the app's access from your Google Account security settings.

Documents and Drive files created or modified through the app remain in your
Google account unless you delete or trash them.

## Security

Never share `token.json`, OAuth authorization codes, refresh tokens, service
account keys, or other private credentials. Review document IDs, permission
changes, deletion ranges, and raw batch update requests before approving
destructive or sharing-related operations.

## Changes

This policy may be updated as the project evolves. Changes will be published in
this repository.

## Contact

For privacy or security questions, contact:

```text
ahmedlaminouamadou@gmail.com
```
