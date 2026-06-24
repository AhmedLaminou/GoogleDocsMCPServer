# Google Docs MCP

This VS Code extension auto-registers the Google Docs MCP Server with GitHub Copilot Agent.

It exposes 100 tools for creating, reading, searching, formatting, sharing,
exporting, organizing, and collaborating on Google Docs.

## Requirements

- VS Code 1.99+
- [`uv`](https://docs.astral.sh/uv/) installed
- A Google account

Normal users do not need their own Google Cloud project. The published Python
package supplies the public Desktop OAuth client identity, while every user
authorizes their own account and stores their token locally.

The extension launches the `google-docs-mcp-server` command from the
`google-docs-mcp-server-ahmedlaminou` PyPI distribution through `uvx`.

## First-time OAuth

Run **Google Docs MCP: Start OAuth Setup** from the Command Palette. A local loopback OAuth flow opens in your browser and stores the token in your OS user configuration directory. Reload VS Code afterward.

## Development

```powershell
npm install
npm run compile
```
