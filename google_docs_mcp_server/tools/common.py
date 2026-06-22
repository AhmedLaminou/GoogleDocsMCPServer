"""Shared helpers for Google Docs and Drive MCP tools."""

from __future__ import annotations

import re
from typing import Any, Iterable


def get_service(api_type: str):
    from google_docs_mcp_server.auth import get_google_service

    return get_google_service(api_type)


def execute(request):
    """Execute a Google API request (kept separate for easy mocking)."""
    return request.execute()


def escape_drive_query(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def iter_structural_elements(elements: Iterable[dict[str, Any]]):
    """Yield structural elements recursively, including table-cell content."""
    for element in elements or []:
        yield element
        table = element.get("table")
        if table:
            for row in table.get("tableRows", []):
                for cell in row.get("tableCells", []):
                    yield from iter_structural_elements(cell.get("content", []))
        toc = element.get("tableOfContents")
        if toc:
            yield from iter_structural_elements(toc.get("content", []))


def iter_text_runs(elements: Iterable[dict[str, Any]]):
    for element in iter_structural_elements(elements):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for paragraph_element in paragraph.get("elements", []):
            text_run = paragraph_element.get("textRun")
            if text_run is not None:
                yield paragraph_element, text_run


def extract_text(elements: Iterable[dict[str, Any]]) -> str:
    return "".join(
        text_run.get("content", "")
        for _, text_run in iter_text_runs(elements)
    )


def document_body(document: dict[str, Any]) -> list[dict[str, Any]]:
    return document.get("body", {}).get("content", [])


def document_end_index(document: dict[str, Any]) -> int:
    content = document_body(document)
    if not content:
        return 1
    return max(1, content[-1].get("endIndex", 2) - 1)


def validate_range(start_idx: int, end_idx: int) -> None:
    if start_idx < 1:
        raise ValueError("start_idx must be at least 1.")
    if end_idx <= start_idx:
        raise ValueError("end_idx must be greater than start_idx.")


def validate_index(index: int) -> None:
    if index < 1:
        raise ValueError("index must be at least 1.")


def validate_rgb(r: float, g: float, b: float) -> None:
    if any(component < 0 or component > 1 for component in (r, g, b)):
        raise ValueError("RGB components must each be between 0 and 1.")


def normalize_items(items: list[str]) -> str:
    if not items:
        raise ValueError("items must contain at least one string.")
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        raise ValueError("items must contain at least one non-empty string.")
    return "\n".join(cleaned) + "\n"


def find_text_ranges(
    document: dict[str, Any],
    target: str,
    match_case: bool = False,
) -> list[dict[str, Any]]:
    if not target:
        raise ValueError("target must not be empty.")

    flags = 0 if match_case else re.IGNORECASE
    matches: list[dict[str, Any]] = []
    for paragraph_element, text_run in iter_text_runs(document_body(document)):
        content = text_run.get("content", "")
        base_index = paragraph_element.get("startIndex", 0)
        for match in re.finditer(re.escape(target), content, flags):
            matches.append(
                {
                    "startIndex": base_index + match.start(),
                    "endIndex": base_index + match.end(),
                    "text": match.group(0),
                }
            )
    return matches


def find_table(document: dict[str, Any], table_index: int) -> dict[str, Any]:
    tables = [
        element["table"]
        for element in document_body(document)
        if "table" in element
    ]
    if table_index < 0 or table_index >= len(tables):
        raise IndexError(
            f"table_index {table_index} is out of range; document contains {len(tables)} tables."
        )
    return tables[table_index]


def table_cell_insert_index(
    document: dict[str, Any],
    table_index: int,
    row_index: int,
    column_index: int,
) -> int:
    table = find_table(document, table_index)
    rows = table.get("tableRows", [])
    if row_index < 0 or row_index >= len(rows):
        raise IndexError(f"row_index {row_index} is out of range.")
    cells = rows[row_index].get("tableCells", [])
    if column_index < 0 or column_index >= len(cells):
        raise IndexError(f"column_index {column_index} is out of range.")

    content = cells[column_index].get("content", [])
    if not content:
        raise ValueError("The selected table cell has no writable paragraph.")
    return content[0].get("startIndex", 0) + 1
