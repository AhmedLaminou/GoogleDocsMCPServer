"""Insertion and batch-update tools."""

from __future__ import annotations

from typing import Any

from google_docs_mcp_server.tools.common import (
    execute,
    get_service,
    normalize_items,
    table_cell_insert_index,
    validate_index,
)


def _batch_update(doc_id: str, requests: list[dict[str, Any]]) -> dict[str, Any]:
    return execute(
        get_service("v1")
        .documents()
        .batchUpdate(documentId=doc_id, body={"requests": requests})
    )


def insert_text(doc_id: str, index: int, text: str) -> dict[str, Any]:
    """Insert text at a UTF-16 document index."""
    validate_index(index)
    response = _batch_update(
        doc_id, [{"insertText": {"location": {"index": index}, "text": text}}]
    )
    return {"document_id": doc_id, "index": index, "inserted_characters": len(text), "response": response}


def insert_page_break(doc_id: str, index: int) -> dict[str, Any]:
    """Insert an explicit page break."""
    validate_index(index)
    response = _batch_update(
        doc_id, [{"insertPageBreak": {"location": {"index": index}}}]
    )
    return {"document_id": doc_id, "index": index, "response": response}


def insert_footnote(doc_id: str, text: str, index: int) -> dict[str, Any]:
    """Create a footnote marker and insert text into the new footnote segment."""
    validate_index(index)
    created = _batch_update(
        doc_id, [{"createFootnote": {"location": {"index": index}}}]
    )
    replies = created.get("replies", [])
    footnote_id = (
        replies[0].get("createFootnote", {}).get("footnoteId") if replies else None
    )
    if not footnote_id:
        raise RuntimeError("Google created no footnote ID.")
    inserted = _batch_update(
        doc_id,
        [
            {
                "insertText": {
                    "endOfSegmentLocation": {"segmentId": footnote_id},
                    "text": text,
                }
            }
        ],
    )
    return {
        "document_id": doc_id,
        "footnote_id": footnote_id,
        "inserted_characters": len(text),
        "response": inserted,
    }


def create_bullet_list(doc_id: str, items: list[str], index: int) -> dict[str, Any]:
    """Insert items and format their paragraphs as a bulleted list."""
    validate_index(index)
    text = normalize_items(items)
    response = _batch_update(
        doc_id,
        [
            {"insertText": {"location": {"index": index}, "text": text}},
            {
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": index + len(text)},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            },
        ],
    )
    return {"document_id": doc_id, "item_count": len(items), "response": response}


def create_numbered_list(doc_id: str, items: list[str], index: int) -> dict[str, Any]:
    """Insert items and format their paragraphs as a numbered list."""
    validate_index(index)
    text = normalize_items(items)
    response = _batch_update(
        doc_id,
        [
            {"insertText": {"location": {"index": index}, "text": text}},
            {
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": index + len(text)},
                    "bulletPreset": "NUMBERED_DECIMAL_ALPHA_ROMAN",
                }
            },
        ],
    )
    return {"document_id": doc_id, "item_count": len(items), "response": response}


def insert_table(
    doc_id: str, rows: int, cols: int, index: int
) -> dict[str, Any]:
    """Insert a blank table."""
    validate_index(index)
    if rows < 1 or cols < 1:
        raise ValueError("rows and cols must both be positive.")
    response = _batch_update(
        doc_id,
        [
            {
                "insertTable": {
                    "rows": rows,
                    "columns": cols,
                    "location": {"index": index},
                }
            }
        ],
    )
    return {"document_id": doc_id, "rows": rows, "columns": cols, "response": response}


def write_table_cell(
    doc_id: str,
    table_index: int,
    row_index: int,
    column_index: int,
    text: str,
    replace_existing: bool = True,
) -> dict[str, Any]:
    """Write into a cell selected by zero-based table, row, and column indexes."""
    service = get_service("v1")
    document = execute(service.documents().get(documentId=doc_id))
    insert_at = table_cell_insert_index(
        document, table_index, row_index, column_index
    )
    table = [
        element["table"]
        for element in document.get("body", {}).get("content", [])
        if "table" in element
    ][table_index]
    cell = table["tableRows"][row_index]["tableCells"][column_index]
    cell_end = max(
        (part.get("endIndex", insert_at + 1) for part in cell.get("content", [])),
        default=insert_at + 1,
    )
    requests: list[dict[str, Any]] = []
    if replace_existing and cell_end - 1 > insert_at:
        requests.append(
            {
                "deleteContentRange": {
                    "range": {"startIndex": insert_at, "endIndex": cell_end - 1}
                }
            }
        )
    requests.append(
        {"insertText": {"location": {"index": insert_at}, "text": text}}
    )
    response = execute(
        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        )
    )
    return {
        "document_id": doc_id,
        "table_index": table_index,
        "row_index": row_index,
        "column_index": column_index,
        "response": response,
    }


def insert_external_image(
    doc_id: str, image_url: str, index: int, width_points: float = 300
) -> dict[str, Any]:
    """Embed a publicly accessible image URL."""
    validate_index(index)
    if width_points <= 0:
        raise ValueError("width_points must be positive.")
    response = _batch_update(
        doc_id,
        [
            {
                "insertInlineImage": {
                    "location": {"index": index},
                    "uri": image_url,
                    "objectSize": {
                        "width": {"magnitude": width_points, "unit": "PT"}
                    },
                }
            }
        ],
    )
    return {"document_id": doc_id, "index": index, "response": response}


def batch_updates(
    doc_id: str, requests_json_array: list[dict[str, Any]]
) -> dict[str, Any]:
    """Execute raw Google Docs batchUpdate requests."""
    if not requests_json_array:
        raise ValueError("requests_json_array must not be empty.")
    if len(requests_json_array) > 100:
        raise ValueError("A maximum of 100 requests is allowed per tool call.")
    return _batch_update(doc_id, requests_json_array)
