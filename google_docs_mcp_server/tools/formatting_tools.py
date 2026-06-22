"""Text, paragraph, and deletion tools."""

from __future__ import annotations

from typing import Any

from google_docs_mcp_server.tools.common import (
    document_end_index,
    execute,
    get_service,
    validate_range,
    validate_rgb,
)


def _batch_update(doc_id: str, requests: list[dict[str, Any]]) -> dict[str, Any]:
    return execute(
        get_service("v1")
        .documents()
        .batchUpdate(documentId=doc_id, body={"requests": requests})
    )


def apply_text_style(
    doc_id: str,
    style_dict: dict[str, Any],
    fields: str,
    start_idx: int,
    end_idx: int,
) -> dict[str, Any]:
    validate_range(start_idx, end_idx)
    return _batch_update(
        doc_id,
        [
            {
                "updateTextStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "textStyle": style_dict,
                    "fields": fields,
                }
            }
        ],
    )


def format_bold(doc_id: str, start_idx: int, end_idx: int, enabled: bool = True):
    return apply_text_style(doc_id, {"bold": enabled}, "bold", start_idx, end_idx)


def format_italic(doc_id: str, start_idx: int, end_idx: int, enabled: bool = True):
    return apply_text_style(doc_id, {"italic": enabled}, "italic", start_idx, end_idx)


def format_underline(doc_id: str, start_idx: int, end_idx: int, enabled: bool = True):
    return apply_text_style(doc_id, {"underline": enabled}, "underline", start_idx, end_idx)


def change_font_family(doc_id: str, font_name: str, start_idx: int, end_idx: int):
    return apply_text_style(
        doc_id,
        {"weightedFontFamily": {"fontFamily": font_name}},
        "weightedFontFamily",
        start_idx,
        end_idx,
    )


def change_font_size(doc_id: str, pt_size: float, start_idx: int, end_idx: int):
    if pt_size <= 0:
        raise ValueError("pt_size must be positive.")
    return apply_text_style(
        doc_id,
        {"fontSize": {"magnitude": pt_size, "unit": "PT"}},
        "fontSize",
        start_idx,
        end_idx,
    )


def change_text_color(
    doc_id: str, r: float, g: float, b: float, start_idx: int, end_idx: int
):
    validate_rgb(r, g, b)
    color = {"color": {"rgbColor": {"red": r, "green": g, "blue": b}}}
    return apply_text_style(
        doc_id, {"foregroundColor": color}, "foregroundColor", start_idx, end_idx
    )


def highlight_text(
    doc_id: str, r: float, g: float, b: float, start_idx: int, end_idx: int
):
    validate_rgb(r, g, b)
    color = {"color": {"rgbColor": {"red": r, "green": g, "blue": b}}}
    return apply_text_style(
        doc_id, {"backgroundColor": color}, "backgroundColor", start_idx, end_idx
    )


def apply_heading_style(
    doc_id: str, heading_enum: str, start_idx: int, end_idx: int
):
    validate_range(start_idx, end_idx)
    return _batch_update(
        doc_id,
        [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "paragraphStyle": {"namedStyleType": heading_enum},
                    "fields": "namedStyleType",
                }
            }
        ],
    )


def set_paragraph_alignment(
    doc_id: str, alignment: str, start_idx: int, end_idx: int
):
    validate_range(start_idx, end_idx)
    allowed = {"START", "CENTER", "END", "JUSTIFIED"}
    if alignment not in allowed:
        raise ValueError(f"alignment must be one of {sorted(allowed)}.")
    return _batch_update(
        doc_id,
        [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "paragraphStyle": {"alignment": alignment},
                    "fields": "alignment",
                }
            }
        ],
    )


def indent_paragraph(
    doc_id: str,
    start_idx: int,
    end_idx: int,
    indent_start_points: float = 36,
    indent_first_line_points: float = 0,
):
    """Set paragraph start and first-line indentation in points."""
    validate_range(start_idx, end_idx)
    if indent_start_points < 0 or indent_first_line_points < 0:
        raise ValueError("Indent values cannot be negative.")
    return _batch_update(
        doc_id,
        [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "paragraphStyle": {
                        "indentStart": {
                            "magnitude": indent_start_points,
                            "unit": "PT",
                        },
                        "indentFirstLine": {
                            "magnitude": indent_first_line_points,
                            "unit": "PT",
                        },
                    },
                    "fields": "indentStart,indentFirstLine",
                }
            }
        ],
    )


def set_line_spacing(
    doc_id: str, spacing_multiplier: float, start_idx: int, end_idx: int
):
    validate_range(start_idx, end_idx)
    if spacing_multiplier <= 0:
        raise ValueError("spacing_multiplier must be positive.")
    return _batch_update(
        doc_id,
        [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx},
                    "paragraphStyle": {"lineSpacing": spacing_multiplier * 100},
                    "fields": "lineSpacing",
                }
            }
        ],
    )


def clear_formatting(doc_id: str, start_idx: int, end_idx: int):
    """Reset common explicit text styles to inherited defaults."""
    fields = (
        "bold,italic,underline,strikethrough,smallCaps,backgroundColor,"
        "foregroundColor,fontSize,weightedFontFamily,baselineOffset,link"
    )
    return apply_text_style(doc_id, {}, fields, start_idx, end_idx)


def delete_text(doc_id: str, start_idx: int, end_idx: int):
    validate_range(start_idx, end_idx)
    return _batch_update(
        doc_id,
        [
            {
                "deleteContentRange": {
                    "range": {"startIndex": start_idx, "endIndex": end_idx}
                }
            }
        ],
    )


def delete_table_row(doc_id: str, table_idx: int, row_idx: int):
    if table_idx < 1 or row_idx < 0:
        raise ValueError("table_idx must be >= 1 and row_idx must be >= 0.")
    return _batch_update(
        doc_id,
        [
            {
                "deleteTableRow": {
                    "tableCellLocation": {
                        "tableStartLocation": {"index": table_idx},
                        "rowIndex": row_idx,
                        "columnIndex": 0,
                    }
                }
            }
        ],
    )


def clear_document(doc_id: str):
    service = get_service("v1")
    document = execute(service.documents().get(documentId=doc_id))
    end_index = document_end_index(document)
    if end_index <= 1:
        return {"document_id": doc_id, "cleared": False, "reason": "already empty"}
    response = execute(
        service.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "deleteContentRange": {
                            "range": {"startIndex": 1, "endIndex": end_index}
                        }
                    }
                ]
            },
        )
    )
    return {"document_id": doc_id, "cleared": True, "response": response}


def undo_last_action(doc_id: str) -> dict[str, Any]:
    """Explain the upstream limitation instead of claiming an unsafe fake undo."""
    return {
        "document_id": doc_id,
        "undone": False,
        "supported": False,
        "message": (
            "Google Docs API does not expose editor undo or revision restore. "
            "Use the Google Docs editor's version history for restoration."
        ),
        "version_history_url": (
            f"https://docs.google.com/document/d/{doc_id}/edit?usp=sharing"
        ),
    }
