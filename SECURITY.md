# Security Policy

## Reporting

Do not open a public issue for credential exposure or another sensitive vulnerability. Use GitHub private vulnerability reporting when available.

## Security Notes

- Never commit `credentials.json`, `token.json`, `.env`, OAuth codes, or refresh tokens.
- The publisher's Desktop OAuth client configuration may be distributed as
  `google_docs_mcp_server/oauth_client.json`; installed-app clients are public
  clients. This never justifies distributing a user's token.
- The configured Google scopes grant full Docs and Drive access.
- Protect public MCP routes with `MCP_API_KEY`, HTTPS, and a host allowlist.
- Store production OAuth tokens in persistent encrypted storage.
- Review document IDs, permission targets, deletion ranges, and raw batch requests before mutation.
