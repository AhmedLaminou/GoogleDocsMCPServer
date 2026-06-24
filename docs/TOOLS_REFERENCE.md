# Google Docs MCP Tool Reference

The server registers **100 unique tools**. Unless noted otherwise, document
indexes are UTF-16 indexes used by the Google Docs API.

## Document and Drive management (27)

1. `create_doc`
2. `delete_doc`
3. `restore_doc`
4. `rename_doc`
5. `copy_doc`
6. `list_recent_docs`
7. `search_docs`
8. `get_doc_metadata`
9. `move_to_folder`
10. `add_to_folder`
11. `remove_from_folder`
12. `create_folder`
13. `list_folders`
14. `list_folder_contents`
15. `export_doc`
16. `export_to_pdf`
17. `share_doc`
18. `unshare_doc`
19. `list_permissions`
20. `update_permission`
21. `list_revisions`
22. `read_full_doc`
23. `append_text`
24. `prepend_text`
25. `replace_document_content`
26. `get_document_end_index`
27. `find_and_replace`

`export_doc` supports `pdf`, `docx`, `odt`, `txt`, `html`, `epub`, and `rtf`.
It returns base64 so remote clients do not need access to the server filesystem.

`move_to_folder` removes existing parents and performs an exclusive move.
`add_to_folder` preserves existing parents.

Drive listing and search only see files available to the active OAuth scope
profile. The default `drive.file` profile cannot enumerate unrelated,
pre-existing Drive content.

## Insertion and writing (9)

1. `insert_text`
2. `insert_page_break`
3. `insert_footnote`
4. `create_bullet_list`
5. `create_numbered_list`
6. `insert_table`
7. `write_table_cell`
8. `insert_external_image`
9. `batch_updates`

External image URLs must be retrievable by Google. Google supports PNG, JPEG,
and GIF images under its documented size and resolution limits.

## Formatting and deletion (22)

1. `format_bold`
2. `format_italic`
3. `format_underline`
4. `format_strikethrough`
5. `format_subscript`
6. `format_superscript`
7. `change_font_family`
8. `change_font_size`
9. `change_text_color`
10. `highlight_text`
11. `apply_heading_style`
12. `set_paragraph_alignment`
13. `indent_paragraph`
14. `set_line_spacing`
15. `set_paragraph_spacing`
16. `set_keep_with_next`
17. `set_paragraph_direction`
18. `clear_formatting`
19. `delete_text`
20. `delete_table_row`
21. `clear_document`
22. `undo_last_action`

RGB components use values from `0.0` to `1.0`.

`delete_table_row.table_idx` is the Google Docs table start index. The newer
advanced table tools use a zero-based table ordinal and resolve the start index
automatically.

`undo_last_action` is an honest capability-report tool: the Google Docs API
does not expose editor undo or revision restoration.

## Extraction and collaboration (17)

1. `read_selection`
2. `read_page`
3. `find_text`
4. `get_headers`
5. `get_footnotes`
6. `read_table_data`
7. `read_links`
8. `create_comment`
9. `reply_to_comment`
10. `list_active_comments`
11. `list_all_comments`
12. `update_comment`
13. `delete_comment`
14. `update_reply`
15. `delete_reply`
16. `resolve_comment`
17. `insert_linked_bookmark`

`read_page` uses explicit page breaks because the API does not expose rendered
physical-page boundaries. `insert_linked_bookmark` creates a named range
because bookmark creation is not exposed.

## Advanced structure, tables, images, and tabs (25)

1. `add_link`
2. `remove_link`
3. `remove_bullets`
4. `insert_table_row`
5. `insert_table_column`
6. `delete_table_column`
7. `merge_table_cells`
8. `unmerge_table_cells`
9. `replace_image`
10. `create_header`
11. `create_footer`
12. `delete_header`
13. `delete_footer`
14. `insert_section_break`
15. `set_page_setup`
16. `list_named_ranges`
17. `delete_named_range`
18. `replace_named_range_content`
19. `get_document_structure`
20. `list_images`
21. `list_tabs`
22. `read_tab`
23. `add_tab`
24. `rename_tab`
25. `delete_tab`

Table ordinals, row indexes, and column indexes in this section are zero-based.

Tab-aware tools use `includeTabsContent=true`. Older body-oriented tools remain
compatible with single-tab documents and operate on the first tab when Google
requires a tab selection.

## Image generation

The core server intentionally does not generate images. Generation introduces
provider credentials, billing, content-policy, and privacy concerns unrelated
to Google Docs. A capable client can generate an image through any provider,
host it at a retrievable URL, then call `insert_external_image` or
`replace_image`.
