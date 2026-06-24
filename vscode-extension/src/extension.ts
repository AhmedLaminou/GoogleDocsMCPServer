import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const startOAuth = vscode.commands.registerCommand(
        'google-docs-mcp.startOAuth',
        async () => {
            const terminal = vscode.window.createTerminal('Google Docs MCP OAuth');
            terminal.sendText(
                'uvx --from google-docs-mcp-server-ahmedlaminou google-docs-mcp-auth login'
            );
            terminal.show();
            void vscode.window.showInformationMessage(
                'Complete Google consent in your browser, then reload VS Code so the MCP server can use your local token.'
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
