"""Advanced structure, table, image, link, and tab tools."""

from __future__ import annotations

from typing import Any

from google_docs_mcp_server.tools.common import (
    document_body,
    execute,
    extract_text,
    find_tab,
    get_service,
    iter_tabs,
    tab_body,
    table_start_index,
    validate_index,
    validate_range,
)


def _batch_update(doc_id: str, requests: list[dict[str, Any]]) -> dict[str, Any]:
    return execute(
        get_service("v1")
        .documents()
        .batchUpdate(documentId=doc_id, body={"requests": requests})
    )


def add_link(
    doc_id: str, start_idx: int, end_idx: int, url: str
) -> dict[str, Any]:
    """Apply a hyperlink to a text range."""
    validate_range(start_idx, end_idx)
    if not url.strip():
        raise ValueError("url must not be empty.")
    return _batch_update(
        doc_id,
        [
            {
                "updateTextStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "textStyle": {"link": {"url": url.strip()}},
                    "fields": "link",
                }
            }
        ],
    )


def remove_link(doc_id: str, start_idx: int, end_idx: int) -> dict[str, Any]:
    """Remove hyperlinks from a text range."""
    validate_range(start_idx, end_idx)
    return _batch_update(
        doc_id,
        [
            {
                "updateTextStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "textStyle": {},
                    "fields": "link",
                }
            }
        ],
    )


def remove_bullets(doc_id: str, start_idx: int, end_idx: int) -> dict[str, Any]:
    """Remove list bullets or numbering from paragraphs in a range."""
    validate_range(start_idx, end_idx)
    return _batch_update(
        doc_id,
        [
            {
                "deleteParagraphBullets": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx}
                }
            }
        ],
    )


def insert_table_row(
    doc_id: str, table_index: int, row_index: int, insert_below: bool = True
) -> dict[str, Any]:
    """Insert a table row using zero-based table and row indexes."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    start = table_start_index(document, table_index)
    return _batch_update(
        doc_id,
        [
            {
                "insertTableRow": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": start},
                        "rowIndex": row_index,
                        "columnIndex": 0,
                    },
                    "insertBelow": insert_below,
                }
            }
        ],
    )


def insert_table_column(
    doc_id: str, table_index: int, column_index: int, insert_right: bool = True
) -> dict[str, Any]:
    """Insert a table column using zero-based table and column indexes."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    start = table_start_index(document, table_index)
    return _batch_update(
        doc_id,
        [
            {
                "insertTableColumn": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": start},
                        "rowIndex": 0,
                        "columnIndex": column_index,
                    },
                    "insertRight": insert_right,
                }
            }
        ],
    )


def delete_table_column(
    doc_id: str, table_index: int, column_index: int
) -> dict[str, Any]:
    """Delete a table column using zero-based table and column indexes."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    start = table_start_index(document, table_index)
    return _batch_update(
        doc_id,
        [
            {
                "deleteTableColumn": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": start},
                        "rowIndex": 0,
                        "columnIndex": column_index,
                    }
                }
            }
        ],
    )


def merge_table_cells(
    doc_id: str,
    table_index: int,
    row_index: int,
    column_index: int,
    row_span: int = 1,
    column_span: int = 2,
) -> dict[str, Any]:
    """Merge a rectangular table-cell range."""
    if row_span < 1 or column_span < 1 or row_span * column_span < 2:
        raise ValueError("The merge range must contain at least two cells.")
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    start = table_start_index(document, table_index)
    return _batch_update(
        doc_id,
        [
            {
                "mergeTableCells": {
                    "tableRange": {
                        "tableCellLocation": {
                            "tableStartLocation": {"index": start},
                            "rowIndex": row_index,
                            "columnIndex": column_index,
                        },
                        "rowSpan": row_span,
                        "columnSpan": column_span,
                    }
                }
            }
        ],
    )


def unmerge_table_cells(
    doc_id: str,
    table_index: int,
    row_index: int,
    column_index: int,
    row_span: int = 1,
    column_span: int = 1,
) -> dict[str, Any]:
    """Unmerge cells intersecting a rectangular table range."""
    if row_span < 1 or column_span < 1:
        raise ValueError("row_span and column_span must be positive.")
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    start = table_start_index(document, table_index)
    return _batch_update(
        doc_id,
        [
            {
                "unmergeTableCells": {
                    "tableRange": {
                        "tableCellLocation": {
                            "tableStartLocation": {"index": start},
                            "rowIndex": row_index,
                            "columnIndex": column_index,
                        },
                        "rowSpan": row_span,
                        "columnSpan": column_span,
                    }
                }
            }
        ],
    )


def replace_image(
    doc_id: str, image_object_id: str, image_url: str, replace_method: str = "CENTER_CROP"
) -> dict[str, Any]:
    """Replace an existing image with a publicly accessible image URL."""
    allowed = {"CENTER_CROP"}
    if replace_method not in allowed:
        raise ValueError(f"replace_method must be one of {sorted(allowed)}.")
    if not image_url.strip():
        raise ValueError("image_url must not be empty.")
    return _batch_update(
        doc_id,
        [
            {
                "replaceImage": {
                    "imageObjectId": image_object_id,
                    "uri": image_url.strip(),
                    "imageReplaceMethod": replace_method,
                }
            }
        ],
    )


def create_header(doc_id: str, section_break_index: int = 0) -> dict[str, Any]:
    """Create a default header for the document or a section."""
    request: dict[str, Any] = {"type": "DEFAULT"}
    if section_break_index:
        validate_index(section_break_index)
        request["sectionBreakLocation"] = {"index": section_break_index}
    return _batch_update(doc_id, [{"createHeader": request}])


def create_footer(doc_id: str, section_break_index: int = 0) -> dict[str, Any]:
    """Create a default footer for the document or a section."""
    request: dict[str, Any] = {"type": "DEFAULT"}
    if section_break_index:
        validate_index(section_break_index)
        request["sectionBreakLocation"] = {"index": section_break_index}
    return _batch_update(doc_id, [{"createFooter": request}])


def delete_header(doc_id: str, header_id: str) -> dict[str, Any]:
    """Delete a header segment."""
    if not header_id.strip():
        raise ValueError("header_id must not be empty.")
    return _batch_update(
        doc_id, [{"deleteHeader": {"headerId": header_id.strip()}}]
    )


def delete_footer(doc_id: str, footer_id: str) -> dict[str, Any]:
    """Delete a footer segment."""
    if not footer_id.strip():
        raise ValueError("footer_id must not be empty.")
    return _batch_update(
        doc_id, [{"deleteFooter": {"footerId": footer_id.strip()}}]
    )


def insert_section_break(
    doc_id: str, index: int, section_type: str = "NEXT_PAGE"
) -> dict[str, Any]:
    """Insert a section break at a document index."""
    validate_index(index)
    allowed = {"NEXT_PAGE", "CONTINUOUS", "UNSPECIFIED"}
    if section_type not in allowed:
        raise ValueError(f"section_type must be one of {sorted(allowed)}.")
    return _batch_update(
        doc_id,
        [
            {
                "insertSectionBreak": {
                    "location": {"index": index},
                    "sectionType": section_type,
                }
            }
        ],
    )


def set_page_setup(
    doc_id: str,
    width_points: float = 612,
    height_points: float = 792,
    margin_top_points: float = 72,
    margin_bottom_points: float = 72,
    margin_left_points: float = 72,
    margin_right_points: float = 72,
) -> dict[str, Any]:
    """Set page size and margins in points."""
    values = (
        width_points,
        height_points,
        margin_top_points,
        margin_bottom_points,
        margin_left_points,
        margin_right_points,
    )
    if any(value < 0 for value in values) or width_points == 0 or height_points == 0:
        raise ValueError("Page dimensions must be positive and margins non-negative.")
    dimension = lambda value: {"magnitude": value, "unit": "PT"}
    style = {
        "pageSize": {
            "width": dimension(width_points),
            "height": dimension(height_points),
        },
        "marginTop": dimension(margin_top_points),
        "marginBottom": dimension(margin_bottom_points),
        "marginLeft": dimension(margin_left_points),
        "marginRight": dimension(margin_right_points),
    }
    return _batch_update(
        doc_id,
        [
            {
                "updateDocumentStyle": {
                    "documentStyle": style,
                    "fields": (
                        "pageSize,marginTop,marginBottom,marginLeft,marginRight"
                    ),
                }
            }
        ],
    )


def list_named_ranges(doc_id: str) -> list[dict[str, Any]]:
    """List all named ranges and their document ranges."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    output: list[dict[str, Any]] = []
    for name, group in document.get("namedRanges", {}).items():
        for named_range in group.get("namedRanges", []):
            output.append(
                {
                    "name": name,
                    "named_range_id": named_range.get("namedRangeId"),
                    "ranges": named_range.get("ranges", []),
                }
            )
    return output


def delete_named_range(
    doc_id: str, named_range_id: str = "", name: str = ""
) -> dict[str, Any]:
    """Delete named ranges by ID or by name."""
    if bool(named_range_id.strip()) == bool(name.strip()):
        raise ValueError("Provide exactly one of named_range_id or name.")
    payload = (
        {"namedRangeId": named_range_id.strip()}
        if named_range_id.strip()
        else {"name": name.strip()}
    )
    return _batch_update(doc_id, [{"deleteNamedRange": payload}])


def replace_named_range_content(
    doc_id: str, text: str, named_range_id: str = "", name: str = ""
) -> dict[str, Any]:
    """Replace the content of named ranges selected by ID or name."""
    if bool(named_range_id.strip()) == bool(name.strip()):
        raise ValueError("Provide exactly one of named_range_id or name.")
    payload: dict[str, Any] = {"text": text}
    if named_range_id.strip():
        payload["namedRangeId"] = named_range_id.strip()
    else:
        payload["namedRangeName"] = name.strip()
    return _batch_update(doc_id, [{"replaceNamedRangeContent": payload}])


def get_document_structure(doc_id: str) -> dict[str, Any]:
    """Return a compact structural summary of a document."""
    document = execute(
        get_service("v1")
        .documents()
        .get(documentId=doc_id, includeTabsContent=True)
    )
    body = document_body(document)
    return {
        "document_id": doc_id,
        "title": document.get("title"),
        "revision_id": document.get("revisionId"),
        "body_elements": len(body),
        "paragraph_count": sum("paragraph" in element for element in body),
        "table_count": sum("table" in element for element in body),
        "header_ids": list(document.get("headers", {})),
        "footer_ids": list(document.get("footers", {})),
        "footnote_ids": list(document.get("footnotes", {})),
        "inline_object_ids": list(document.get("inlineObjects", {})),
        "positioned_object_ids": list(document.get("positionedObjects", {})),
        "named_range_names": list(document.get("namedRanges", {})),
        "tabs": [
            {
                "tab_id": tab.get("tabProperties", {}).get("tabId"),
                "title": tab.get("tabProperties", {}).get("title"),
                "index": tab.get("tabProperties", {}).get("index"),
                "parent_tab_id": tab.get("tabProperties", {}).get("parentTabId"),
            }
            for tab in iter_tabs(document.get("tabs", []))
        ],
    }


def list_images(doc_id: str) -> list[dict[str, Any]]:
    """List inline and positioned image/object metadata."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    images: list[dict[str, Any]] = []
    for object_id, inline in document.get("inlineObjects", {}).items():
        embedded = inline.get("inlineObjectProperties", {}).get("embeddedObject", {})
        images.append(
            {
                "object_id": object_id,
                "placement": "inline",
                "title": embedded.get("title"),
                "description": embedded.get("description"),
                "size": embedded.get("size"),
                "source_uri": embedded.get("imageProperties", {}).get("sourceUri"),
                "content_uri": embedded.get("imageProperties", {}).get("contentUri"),
            }
        )
    for object_id, positioned in document.get("positionedObjects", {}).items():
        embedded = positioned.get("positionedObjectProperties", {}).get(
            "embeddedObject", {}
        )
        images.append(
            {
                "object_id": object_id,
                "placement": "positioned",
                "title": embedded.get("title"),
                "description": embedded.get("description"),
                "size": embedded.get("size"),
                "source_uri": embedded.get("imageProperties", {}).get("sourceUri"),
                "content_uri": embedded.get("imageProperties", {}).get("contentUri"),
            }
        )
    return images


def list_tabs(doc_id: str) -> list[dict[str, Any]]:
    """List document tabs recursively."""
    document = execute(
        get_service("v1")
        .documents()
        .get(documentId=doc_id, includeTabsContent=True)
    )
    return [
        {
            "tab_id": tab.get("tabProperties", {}).get("tabId"),
            "title": tab.get("tabProperties", {}).get("title"),
            "index": tab.get("tabProperties", {}).get("index"),
            "parent_tab_id": tab.get("tabProperties", {}).get("parentTabId"),
        }
        for tab in iter_tabs(document.get("tabs", []))
    ]


def read_tab(doc_id: str, tab_id: str) -> dict[str, Any]:
    """Read all text from one document tab."""
    document = execute(
        get_service("v1")
        .documents()
        .get(documentId=doc_id, includeTabsContent=True)
    )
    tab = find_tab(document, tab_id)
    properties = tab.get("tabProperties", {})
    return {
        "tab_id": tab_id,
        "title": properties.get("title"),
        "text": extract_text(tab_body(tab)),
    }


def add_tab(doc_id: str, title: str, parent_tab_id: str = "") -> dict[str, Any]:
    """Add a document tab."""
    tab_title = title.strip()
    if not tab_title:
        raise ValueError("title must not be empty.")
    properties: dict[str, Any] = {"title": tab_title}
    if parent_tab_id.strip():
        properties["parentTabId"] = parent_tab_id.strip()
    return _batch_update(
        doc_id, [{"addDocumentTab": {"tabProperties": properties}}]
    )


def rename_tab(doc_id: str, tab_id: str, new_title: str) -> dict[str, Any]:
    """Rename a document tab."""
    title = new_title.strip()
    if not title:
        raise ValueError("new_title must not be empty.")
    return _batch_update(
        doc_id,
        [
            {
                "updateDocumentTabProperties": {
                    "tabProperties": {"tabId": tab_id, "title": title},
                    "fields": "title",
                }
            }
        ],
    )


def delete_tab(doc_id: str, tab_id: str) -> dict[str, Any]:
    """Delete a document tab."""
    return _batch_update(doc_id, [{"deleteTab": {"tabId": tab_id}}])
