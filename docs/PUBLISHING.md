# Publishing Guide

## GitHub

The canonical repository is:

```text
https://github.com/AhmedLaminou/GoogleDocsMCPServer
```

## Verify

```powershell
pip install -e .
python -m unittest discover -s tests -v
python -m compileall google_docs_mcp_server

cd vscode-extension
npm install
npm run compile
cd ..
```

Confirm that `google_docs_mcp_server/oauth_client.json` is a **Desktop app**
OAuth client belonging to the production Google Cloud project. Never include a
user token.

Before public release, complete Google OAuth verification for the sensitive
`documents` scope. Keep the public profile on `drive.file`; do not silently
switch it to restricted full-Drive access.

## PyPI

```powershell
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

The distribution name is `google-docs-mcp-server`.

The README marker must exactly match `server.json`:

```html
<!-- mcp-name: io.github.AhmedLaminou/google-docs-mcp-server -->
```

## MCP Registry

After the PyPI release exists:

```powershell
mcp-publisher login github
mcp-publisher publish
```

## VS Code Marketplace

Create a Visual Studio Marketplace publisher named `ahmedlaminou`, then:

```powershell
cd vscode-extension
npm install
npm run package
npx vsce publish
```

Update the Python package, `server.json`, extension, and changelog versions together.
