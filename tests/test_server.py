from __future__ import annotations

import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import httplib2
from fastapi.testclient import TestClient
from googleapiclient.errors import HttpError

import main
from google_docs_mcp_server import auth
from google_docs_mcp_server.tools import (
    advanced_tools,
    docs_tools,
    extraction_tools,
    formatting_tools,
    insertion_tools,
)
from google_docs_mcp_server.tools.common import (
    execute as common_execute,
    extract_text,
    find_text_ranges,
    table_cell_insert_index,
    table_start_index,
)
from google_docs_mcp_server.registry import TOOL_FUNCTIONS


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

    def execute(self, **_kwargs):
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
    def test_exactly_one_hundred_unique_tools_are_registered(self):
        tools = asyncio.run(main.mcp.list_tools())
        self.assertEqual(100, len(tools))
        self.assertEqual(100, len({tool.name for tool in tools}))
        self.assertEqual(100, len(TOOL_FUNCTIONS))

    def test_health_reports_auth_and_tool_count(self):
        response = TestClient(main.app).get("/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual("ok", response.json()["status"])
        self.assertEqual(100, response.json()["tool_count"])

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

    def test_api_http_timeout_is_configurable(self):
        with patch.dict(os.environ, {"GOOGLE_DOCS_MCP_HTTP_TIMEOUT": "30"}):
            self.assertEqual(30, auth.api_http_timeout_seconds())
        with patch.dict(os.environ, {"GOOGLE_DOCS_MCP_HTTP_TIMEOUT": "0"}):
            with self.assertRaisesRegex(ValueError, "at least 1"):
                auth.api_http_timeout_seconds()


class CommonHelperTests(unittest.TestCase):
    def test_execute_passes_configured_retry_count(self):
        request = MagicMock()
        request.execute.return_value = {"ok": True}
        with patch.dict(os.environ, {"GOOGLE_DOCS_MCP_API_RETRIES": "4"}):
            self.assertEqual({"ok": True}, common_execute(request))
        request.execute.assert_called_once_with(num_retries=4)

    def test_execute_wraps_google_http_errors(self):
        request = MagicMock()
        response = httplib2.Response({"status": "403", "reason": "Forbidden"})
        request.execute.side_effect = HttpError(response, b'{"error":"denied"}')
        with self.assertRaisesRegex(RuntimeError, "Google API request failed"):
            common_execute(request)

    def test_execute_wraps_timeouts(self):
        request = MagicMock()
        request.execute.side_effect = TimeoutError("slow")
        with self.assertRaisesRegex(TimeoutError, "Google API request timed out"):
            common_execute(request)

    def test_extract_text_includes_table_cells(self):
        self.assertEqual("Hello world\ncell", extract_text(SAMPLE_DOCUMENT["body"]["content"]))

    def test_find_text_returns_document_indexes(self):
        self.assertEqual(
            [{"startIndex": 7, "endIndex": 12, "text": "world"}],
            find_text_ranges(SAMPLE_DOCUMENT, "WORLD"),
        )

    def test_table_cell_insert_index(self):
        self.assertEqual(16, table_cell_insert_index(SAMPLE_DOCUMENT, 0, 0, 0))

    def test_table_start_index(self):
        self.assertEqual(13, table_start_index(SAMPLE_DOCUMENT, 0))


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

    def test_rename_doc_uses_drive_file_update(self):
        service = MagicMock()
        service.files.return_value.update.return_value = FakeRequest(
            {"id": "doc", "name": "Renamed"}
        )
        with patch.object(docs_tools, "get_service", return_value=service):
            result = docs_tools.rename_doc("doc", "Renamed")
        self.assertEqual("Renamed", result["name"])
        service.files.return_value.update.assert_called_once_with(
            fileId="doc",
            body={"name": "Renamed"},
            fields="id,name,modifiedTime,webViewLink",
        )

    def test_restore_doc_clears_trashed_flag(self):
        service = MagicMock()
        service.files.return_value.update.return_value = FakeRequest(
            {"id": "doc", "trashed": False}
        )
        with patch.object(docs_tools, "get_service", return_value=service):
            result = docs_tools.restore_doc("doc")
        self.assertFalse(result["trashed"])

    def test_add_to_folder_preserves_existing_parents(self):
        service = MagicMock()
        service.files.return_value.update.return_value = FakeRequest(
            {"id": "doc", "parents": ["old", "new"]}
        )
        with patch.object(docs_tools, "get_service", return_value=service):
            docs_tools.add_to_folder("doc", "new")
        kwargs = service.files.return_value.update.call_args.kwargs
        self.assertEqual("new", kwargs["addParents"])
        self.assertNotIn("removeParents", kwargs)

    def test_export_doc_validates_format(self):
        with self.assertRaisesRegex(ValueError, "output_format"):
            docs_tools.export_doc("doc", "pages")

    def test_replace_document_content_deletes_then_inserts(self):
        documents = MagicMock()
        documents.get.return_value = FakeRequest(SAMPLE_DOCUMENT)
        documents.batchUpdate.return_value = FakeRequest({"replies": [{}, {}]})
        service = MagicMock()
        service.documents.return_value = documents
        with patch.object(docs_tools, "get_service", return_value=service):
            docs_tools.replace_document_content("doc", "Replacement")
        requests = documents.batchUpdate.call_args.kwargs["body"]["requests"]
        self.assertIn("deleteContentRange", requests[0])
        self.assertEqual("Replacement", requests[1]["insertText"]["text"])

    def test_add_link_request_shape(self):
        with patch.object(
            advanced_tools, "_batch_update", return_value={"replies": []}
        ) as batch:
            advanced_tools.add_link("doc", 1, 5, "https://example.com")
        update = batch.call_args.args[1][0]["updateTextStyle"]
        self.assertEqual("https://example.com", update["textStyle"]["link"]["url"])

    def test_insert_table_row_resolves_ordinal_table(self):
        documents = MagicMock()
        documents.get.return_value = FakeRequest(SAMPLE_DOCUMENT)
        service = MagicMock()
        service.documents.return_value = documents
        with (
            patch.object(advanced_tools, "get_service", return_value=service),
            patch.object(
                advanced_tools, "_batch_update", return_value={"replies": []}
            ) as batch,
        ):
            advanced_tools.insert_table_row("doc", 0, 0)
        location = batch.call_args.args[1][0]["insertTableRow"][
            "tableCellLocation"
        ]
        self.assertEqual(13, location["tableStartLocation"]["index"])

    def test_named_range_requires_exactly_one_selector(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            advanced_tools.delete_named_range("doc")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            advanced_tools.delete_named_range(
                "doc", named_range_id="id", name="name"
            )

    def test_page_setup_validates_dimensions(self):
        with self.assertRaisesRegex(ValueError, "dimensions"):
            advanced_tools.set_page_setup("doc", width_points=0)

    def test_comment_update_rejects_empty_content(self):
        with self.assertRaisesRegex(ValueError, "text"):
            extraction_tools.update_comment("doc", "comment", " ")


if __name__ == "__main__":
    unittest.main()
