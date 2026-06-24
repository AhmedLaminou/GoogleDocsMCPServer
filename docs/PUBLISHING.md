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
OAuth client belonging to the production Google Cloud project. The path is
ignored by Git but intentionally included in release artifacts. Never include a
user token.

The Hatch `artifacts` rule includes this one ignored public-client file when it
is present. Always inspect both the wheel and source archive before upload.

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

The distribution name is `google-docs-mcp-server-ahmedlaminou`. The shorter
`google-docs-mcp-server` name is owned by another PyPI publisher.

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

The existing Visual Studio Marketplace publisher is `ahmedlaminou`:

```powershell
cd vscode-extension
npm install
npm run package
npx vsce publish
```

It is already used by the related Windows Management MCP extension.

Update the Python package, `server.json`, extension, and changelog versions together.
