from __future__ import annotations

import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from google_docs_mcp_server import auth
from google_docs_mcp_server.tools import (
    extraction_tools,
    formatting_tools,
    insertion_tools,
)
from google_docs_mcp_server.tools.common import (
    extract_text,
    find_text_ranges,
    table_cell_insert_index,
)


SAMPLE_DOCUMENT = {
    "body": {
        "content": [
            {
                "startIndex": 1,
                "endIndex": 13,
                "paragraph": {
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "elements": [
                        {
                            "startIndex": 1,
                            "endIndex": 7,
                            "textRun": {"content": "Hello "},
                        },
                        {
                            "startIndex": 7,
                            "endIndex": 13,
                            "textRun": {
                                "content": "world\n",
                                "textStyle": {"link": {"url": "https://example.com"}},
                            },
                        },
                    ],
                },
            },
            {
                "startIndex": 13,
                "endIndex": 20,
                "table": {
                    "tableRows": [
                        {
                            "tableCells": [
                                {
                                    "content": [
                                        {
                                            "startIndex": 15,
                                            "endIndex": 20,
                                            "paragraph": {
                                                "elements": [
                                                    {
                                                        "startIndex": 16,
                                                        "endIndex": 20,
                                                        "textRun": {
                                                            "content": "cell"
                                                        },
                                                    }
                                                ]
                                            },
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
            },
        ]
    },
    "footnotes": {
        "footnote-1": {
            "content": [
                {
                    "paragraph": {
                        "elements": [{"textRun": {"content": "Footnote text"}}]
                    }
                }
            ]
        }
    },
}


class FakeRequest:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class FakeDocuments:
    def __init__(self, document):
        self.document = document

    def get(self, **_kwargs):
        return FakeRequest(self.document)


class FakeDocsService:
    def __init__(self, document):
        self._documents = FakeDocuments(document)

    def documents(self):
        return self._documents


class ServerTests(unittest.TestCase):
    def test_exactly_fifty_unique_tools_are_registered(self):
        tools = asyncio.run(main.mcp.list_tools())
        self.assertEqual(50, len(tools))
        self.assertEqual(50, len({tool.name for tool in tools}))

    def test_health_reports_auth_and_tool_count(self):
        response = TestClient(main.app).get("/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])
        self.assertEqual(50, response.json()["tool_count"])

    def test_optional_api_key_protects_transport(self):
        with patch.dict(os.environ, {"MCP_API_KEY": "secret"}):
            client = TestClient(main.app)
            response = client.get("/sse")
            self.assertEqual(401, response.status_code)
            self.assertEqual(
                "Invalid or missing MCP API key.", response.json()["detail"]
            )

    def test_oauth_callback_rejects_missing_session_state(self):
        response = TestClient(main.app).get(
            "/oauth2callback?state=bad&code=bad"
        )
        self.assertEqual(400, response.status_code)

    def test_public_scope_profile_avoids_restricted_full_drive(self):
        scopes = auth.scopes_for_profile("default")
        self.assertIn(auth.DOCS_SCOPE, scopes)
        self.assertIn(auth.DRIVE_FILE_SCOPE, scopes)
        self.assertNotIn(auth.FULL_DRIVE_SCOPE, scopes)

    def test_full_profile_is_explicit(self):
        self.assertEqual(
            [auth.DOCS_SCOPE, auth.FULL_DRIVE_SCOPE],
            auth.scopes_for_profile("full"),
        )

    def test_local_auth_uses_stable_config_directory(self):
        self.assertNotEqual(Path.cwd() / "token.json", auth.TOKEN_FILE)

    def test_local_auth_rejects_web_client(self):
        with patch.object(
            auth,
            "load_oauth_client_config",
            return_value={"web": {"client_id": "test"}},
        ):
            with self.assertRaisesRegex(RuntimeError, "Desktop app"):
                auth.load_desktop_oauth_client_config()

    def test_local_auth_accepts_desktop_client(self):
        config = {"installed": {"client_id": "test", "client_secret": "test"}}
        with patch.object(auth, "load_oauth_client_config", return_value=config):
            self.assertEqual(config, auth.load_desktop_oauth_client_config())


class CommonHelperTests(unittest.TestCase):
    def test_extract_text_includes_table_cells(self):
        self.assertEqual("Hello world\ncell", extract_text(SAMPLE_DOCUMENT["body"]["content"]))

    def test_find_text_returns_document_indexes(self):
        self.assertEqual(
            [{"startIndex": 7, "endIndex": 12, "text": "world"}],
            find_text_ranges(SAMPLE_DOCUMENT, "WORLD"),
        )

    def test_table_cell_insert_index(self):
        self.assertEqual(16, table_cell_insert_index(SAMPLE_DOCUMENT, 0, 0, 0))


class ToolBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeDocsService(SAMPLE_DOCUMENT)

    def test_read_selection_slices_partial_runs(self):
        with patch.object(extraction_tools, "get_service", return_value=self.service):
            self.assertEqual("lo wor", extraction_tools.read_selection("doc", 4, 10))

    def test_read_footnotes(self):
        with patch.object(extraction_tools, "get_service", return_value=self.service):
            self.assertEqual(
                [{"footnote_id": "footnote-1", "text": "Footnote text"}],
                extraction_tools.get_footnotes("doc"),
            )

    def test_bullet_list_inserts_content_before_formatting(self):
        with patch.object(
            insertion_tools, "_batch_update", return_value={"replies": []}
        ) as batch:
            insertion_tools.create_bullet_list("doc", ["One", "Two"], 5)
        requests = batch.call_args.args[1]
        self.assertEqual("One\nTwo\n", requests[0]["insertText"]["text"])
        self.assertEqual(
            {"startIndex": 5, "endIndex": 13},
            requests[1]["createParagraphBullets"]["range"],
        )

    def test_clear_formatting_uses_nonempty_field_mask(self):
        with patch.object(
            formatting_tools, "_batch_update", return_value={"replies": []}
        ) as batch:
            formatting_tools.clear_formatting("doc", 1, 5)
        update = batch.call_args.args[1][0]["updateTextStyle"]
        self.assertTrue(update["fields"])
        self.assertNotEqual("*", update["fields"])

    def test_undo_is_honest_about_api_limitation(self):
        result = formatting_tools.undo_last_action("doc")
        self.assertFalse(result["undone"])
        self.assertFalse(result["supported"])


if __name__ == "__main__":
    unittest.main()
