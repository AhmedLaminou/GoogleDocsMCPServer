# Terms of Service

Last updated: 2026-06-24

These Terms describe the expected use of Google Docs MCP Server, an open-source
local MCP server for Google Docs and Google Drive automation.

## Use of the Software

You may use the software to connect compatible MCP clients to your own Google
account and perform Google Docs and Drive actions through the available MCP
tools.

You are responsible for the prompts, tool calls, document IDs, sharing targets,
OAuth scopes, and actions you authorize.

## Google Account and API Access

The software uses Google OAuth. By authenticating, you authorize the app to use
the Google scopes shown on the consent screen.

The default public profile requests Google Docs access and per-file Drive access
through `drive.file`. Optional full-Drive mode is available only when you
explicitly use the `--full-drive` profile.

Your use of Google Docs, Google Drive, and Google APIs is also subject to
Google's terms and policies.

## Acceptable Use

Do not use this software to:

- Access, modify, export, or share documents you are not authorized to use.
- Violate laws, regulations, platform rules, or third-party rights.
- Circumvent Google account, Workspace, or administrator restrictions.
- Store or distribute private credentials, tokens, or secrets.
- Operate a hosted service without appropriate authentication, authorization,
  token storage, user consent, and security controls.

## Local and Hosted Operation

The default architecture is local stdio. In that mode, the server runs on your
machine and stores your Google OAuth token locally.

The repository also includes optional hosted/SSE support for controlled
deployments. Hosted operators are responsible for their own security,
compliance, privacy policy, token storage, and user management.

## AI Client Behavior

Google Docs MCP Server exposes tools to an MCP-compatible client. The behavior
of the AI client, including prompts, model outputs, telemetry, and tool-choice
logic, is controlled by that client and its operator. Review tool calls before
approving sensitive, destructive, or sharing-related actions.

## No Warranty

The software is provided as-is, without warranties of any kind. It may contain
bugs, incomplete features, API limitations, or behavior changes caused by
upstream Google APIs, MCP clients, package managers, or platform policies.

## Limitation of Liability

To the maximum extent permitted by law, the project maintainers are not liable
for data loss, unauthorized sharing, account issues, business interruption,
damages, or other consequences arising from use or misuse of the software.

## Open-Source License

The software is distributed under the MIT License. See the repository's
`LICENSE` file for license terms.

## Changes

These Terms may be updated as the project evolves. Changes will be published in
this repository.

## Contact

For questions about these Terms, contact:

```text
ahmedlaminouamadou@gmail.com
```
