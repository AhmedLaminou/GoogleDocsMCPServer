# Contributing

## Development

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .
python -m unittest discover -s tests -v
python -m compileall google_docs_mcp_server
```

For the VS Code extension:

```powershell
cd vscode-extension
npm install
npm run compile
```

## Tool Changes

- Add tools under `google_docs_mcp_server/tools/`.
- Register them in `google_docs_mcp_server/registry.py`.
- Keep destructive actions explicit and narrowly scoped.
- Update `docs/TOOLS_REFERENCE.md` and tests.

## Pull Requests

Include what changed, affected tools, verification commands, and any Google OAuth or API implications.
