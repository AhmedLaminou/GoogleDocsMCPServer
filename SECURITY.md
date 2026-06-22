# Security Policy

## Reporting

Do not open a public issue for credential exposure or another sensitive vulnerability. Use GitHub private vulnerability reporting when available.

## Security Notes

- Never commit `credentials.json`, `token.json`, `.env`, OAuth codes, or refresh tokens.
- The configured Google scopes grant full Docs and Drive access.
- Protect public MCP routes with `MCP_API_KEY`, HTTPS, and a host allowlist.
- Store production OAuth tokens in persistent encrypted storage.
- Review document IDs, permission targets, deletion ranges, and raw batch requests before mutation.
