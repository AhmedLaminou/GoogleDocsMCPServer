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
