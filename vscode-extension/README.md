# Google Docs MCP

This VS Code extension auto-registers the Google Docs MCP Server with GitHub Copilot Agent.

It exposes 50 tools for creating, reading, searching, formatting, sharing, exporting, and collaborating on Google Docs.

## Requirements

- VS Code 1.99+
- [`uv`](https://docs.astral.sh/uv/) installed
- A Google Cloud OAuth web client with the Docs and Drive APIs enabled

The extension launches `google-docs-mcp-server` through `uvx`.

## First-time OAuth

Run **Google Docs MCP: Start OAuth Setup** from the Command Palette. A local loopback OAuth flow opens in your browser and stores the token in your OS user configuration directory. Reload VS Code afterward.

## Development

```powershell
npm install
npm run compile
```
