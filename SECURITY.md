# Security Policy

## Reporting

Do not open a public issue for credential exposure or another sensitive vulnerability. Use GitHub private vulnerability reporting when available.

## Security Notes

- Never commit `credentials.json`, `token.json`, `.env`, OAuth codes, or refresh tokens.
- The publisher's Desktop OAuth client configuration may be distributed as
  `google_docs_mcp_server/oauth_client.json`; the path is ignored by Git and
  installed-app clients are public clients. This never justifies distributing
  a user's token.
- Inject the production Desktop OAuth JSON only into release builds. Verify
  wheel contents before upload and rotate the client if its configuration was
  accidentally disclosed outside the intended public package.
- The default scopes grant Google Docs access plus per-file `drive.file`
  access. Restricted full-Drive access is an explicit self-hosted profile.
- Protect public MCP routes with `MCP_API_KEY`, HTTPS, and a host allowlist.
- Store production OAuth tokens in persistent encrypted storage.
- Review document IDs, permission targets, deletion ranges, and raw batch requests before mutation.
