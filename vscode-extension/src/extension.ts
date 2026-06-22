import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const startOAuth = vscode.commands.registerCommand(
        'google-docs-mcp.startOAuth',
        async () => {
            const terminal = vscode.window.createTerminal('Google Docs MCP OAuth');
            terminal.sendText('uvx --from google-docs-mcp-server google-docs-mcp-web');
            terminal.show();
            await vscode.env.openExternal(vscode.Uri.parse('http://localhost:8000/login'));
            void vscode.window.showInformationMessage(
                'Complete Google consent in your browser, then keep token.json in the MCP working directory or set GOOGLE_TOKEN_FILE.'
            );
        }
    );

    const restart = vscode.commands.registerCommand(
        'google-docs-mcp.restartServer',
        async () => {
            await vscode.commands.executeCommand('workbench.action.reloadWindow');
        }
    );

    context.subscriptions.push(startOAuth, restart);
}

export function deactivate() {}
