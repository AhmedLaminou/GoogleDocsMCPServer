"""Central registry for all Google Docs MCP tools."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from google_docs_mcp_server.tools import (
    docs_tools,
    extraction_tools,
    formatting_tools,
    insertion_tools,
)

TOOL_FUNCTIONS: tuple[Callable[..., Any], ...] = (
    docs_tools.create_doc,
    docs_tools.delete_doc,
    docs_tools.copy_doc,
    docs_tools.list_recent_docs,
    docs_tools.search_docs,
    docs_tools.get_doc_metadata,
    docs_tools.move_to_folder,
    docs_tools.export_to_pdf,
    docs_tools.share_doc,
    docs_tools.unshare_doc,
    docs_tools.read_full_doc,
    docs_tools.append_text,
    docs_tools.find_and_replace,
    insertion_tools.insert_text,
    insertion_tools.insert_page_break,
    insertion_tools.insert_footnote,
    insertion_tools.create_bullet_list,
    insertion_tools.create_numbered_list,
    insertion_tools.insert_table,
    insertion_tools.write_table_cell,
    insertion_tools.insert_external_image,
    insertion_tools.batch_updates,
    formatting_tools.format_bold,
    formatting_tools.format_italic,
    formatting_tools.format_underline,
    formatting_tools.change_font_family,
    formatting_tools.change_font_size,
    formatting_tools.change_text_color,
    formatting_tools.highlight_text,
    formatting_tools.apply_heading_style,
    formatting_tools.set_paragraph_alignment,
    formatting_tools.indent_paragraph,
    formatting_tools.set_line_spacing,
    formatting_tools.clear_formatting,
    formatting_tools.delete_text,
    formatting_tools.delete_table_row,
    formatting_tools.clear_document,
    formatting_tools.undo_last_action,
    extraction_tools.read_selection,
    extraction_tools.read_page,
    extraction_tools.find_text,
    extraction_tools.get_headers,
    extraction_tools.get_footnotes,
    extraction_tools.read_table_data,
    extraction_tools.read_links,
    extraction_tools.create_comment,
    extraction_tools.reply_to_comment,
    extraction_tools.list_active_comments,
    extraction_tools.resolve_comment,
    extraction_tools.insert_linked_bookmark,
)


def register_all_tools(mcp) -> None:
    for function in TOOL_FUNCTIONS:
        mcp.add_tool(function)
