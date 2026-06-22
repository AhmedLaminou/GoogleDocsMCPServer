# Google Docs MCP Tool Reference

The server registers **50 unique tools**.

## Document and Drive Management (13)

1. `create_doc(title)`
2. `delete_doc(doc_id)`
3. `copy_doc(doc_id, new_title)`
4. `list_recent_docs(limit=10)`
5. `search_docs(query, limit=20)`
6. `get_doc_metadata(doc_id)`
7. `move_to_folder(doc_id, folder_id)`
8. `export_to_pdf(doc_id, max_bytes=10000000)`
9. `share_doc(doc_id, email, role="writer")`
10. `unshare_doc(doc_id, email)`
11. `read_full_doc(doc_id)`
12. `append_text(doc_id, text)`
13. `find_and_replace(doc_id, old_text, new_text, match_case=False)`

`export_to_pdf` returns a base64 PDF payload so remote MCP clients can receive the file without relying on the server's filesystem.

## Insertion and Writing (9)

1. `insert_text(doc_id, index, text)`
2. `insert_page_break(doc_id, index)`
3. `insert_footnote(doc_id, text, index)`
4. `create_bullet_list(doc_id, items, index)`
5. `create_numbered_list(doc_id, items, index)`
6. `insert_table(doc_id, rows, cols, index)`
7. `write_table_cell(doc_id, table_index, row_index, column_index, text, replace_existing=True)`
8. `insert_external_image(doc_id, image_url, index, width_points=300)`
9. `batch_updates(doc_id, requests_json_array)`

Table, row, and column selectors in `write_table_cell` are zero-based.

## Formatting and Operations (16)

1. `format_bold(doc_id, start_idx, end_idx, enabled=True)`
2. `format_italic(doc_id, start_idx, end_idx, enabled=True)`
3. `format_underline(doc_id, start_idx, end_idx, enabled=True)`
4. `change_font_family(doc_id, font_name, start_idx, end_idx)`
5. `change_font_size(doc_id, pt_size, start_idx, end_idx)`
6. `change_text_color(doc_id, r, g, b, start_idx, end_idx)`
7. `highlight_text(doc_id, r, g, b, start_idx, end_idx)`
8. `apply_heading_style(doc_id, heading_enum, start_idx, end_idx)`
9. `set_paragraph_alignment(doc_id, alignment, start_idx, end_idx)`
10. `indent_paragraph(doc_id, start_idx, end_idx, indent_start_points=36, indent_first_line_points=0)`
11. `set_line_spacing(doc_id, spacing_multiplier, start_idx, end_idx)`
12. `clear_formatting(doc_id, start_idx, end_idx)`
13. `delete_text(doc_id, start_idx, end_idx)`
14. `delete_table_row(doc_id, table_idx, row_idx)`
15. `clear_document(doc_id)`
16. `undo_last_action(doc_id)`

RGB components use values from `0.0` to `1.0`. `delete_table_row.table_idx` is the Google Docs table start index, not an ordinal.

`undo_last_action` is a capability-report tool because Google exposes no editor undo or revision-restore API.

## Extraction and Collaboration (12)

1. `read_selection(doc_id, start_idx, end_idx)`
2. `read_page(doc_id, page_index)`
3. `find_text(doc_id, target_string, match_case=False)`
4. `get_headers(doc_id)`
5. `get_footnotes(doc_id)`
6. `read_table_data(doc_id)`
7. `read_links(doc_id)`
8. `create_comment(doc_id, text, context_text="")`
9. `reply_to_comment(doc_id, comment_id, reply_text)`
10. `list_active_comments(doc_id)`
11. `resolve_comment(doc_id, comment_id)`
12. `insert_linked_bookmark(doc_id, index, bookmark_name)`

`read_page` uses explicit page breaks. `insert_linked_bookmark` creates a named range because bookmark creation is not exposed by the Docs API.
