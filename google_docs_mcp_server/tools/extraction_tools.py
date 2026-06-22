"""Reading, extraction, comments, and named-range tools."""

from __future__ import annotations

from typing import Any

from google_docs_mcp_server.tools.common import (
    document_body,
    execute,
    extract_text,
    find_text_ranges,
    get_service,
    iter_text_runs,
    validate_index,
    validate_range,
)


def read_selection(doc_id: str, start_idx: int, end_idx: int) -> str:
    """Read the exact overlap of text runs with a UTF-16 index range."""
    validate_range(start_idx, end_idx)
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    pieces: list[str] = []
    for paragraph_element, text_run in iter_text_runs(document_body(document)):
        run_start = paragraph_element.get("startIndex", 0)
        content = text_run.get("content", "")
        run_end = paragraph_element.get("endIndex", run_start + len(content))
        overlap_start = max(start_idx, run_start)
        overlap_end = min(end_idx, run_end)
        if overlap_start < overlap_end:
            pieces.append(content[overlap_start - run_start : overlap_end - run_start])
    return "".join(pieces)


def read_page(doc_id: str, page_index: int) -> dict[str, Any]:
    """Read a logical page separated by explicit page-break elements.

    Google Docs API does not expose rendered physical-page boundaries, so this
    tool intentionally uses explicit page breaks only.
    """
    if page_index < 0:
        raise ValueError("page_index must be zero or greater.")
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    pages: list[list[str]] = [[]]
    for element in document_body(document):
        paragraph = element.get("paragraph")
        if not paragraph:
            if "table" in element:
                pages[-1].append(extract_text([element]))
            continue
        for part in paragraph.get("elements", []):
            if "pageBreak" in part:
                pages.append([])
            elif "textRun" in part:
                pages[-1].append(part["textRun"].get("content", ""))
    if page_index >= len(pages):
        raise IndexError(
            f"page_index {page_index} is out of range; {len(pages)} logical pages found."
        )
    return {
        "page_index": page_index,
        "page_count": len(pages),
        "boundary_type": "explicit_page_break",
        "text": "".join(pages[page_index]),
    }


def find_text(
    doc_id: str, target_string: str, match_case: bool = False
) -> list[dict[str, Any]]:
    """Find exact text occurrences and return their document ranges."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    return find_text_ranges(document, target_string, match_case)


def get_headers(doc_id: str) -> list[dict[str, Any]]:
    """Extract heading paragraphs and their ranges."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    headers: list[dict[str, Any]] = []
    for element in document_body(document):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        style = paragraph.get("paragraphStyle", {}).get("namedStyleType", "")
        if not style.startswith("HEADING_"):
            continue
        text = "".join(
            part.get("textRun", {}).get("content", "")
            for part in paragraph.get("elements", [])
        ).strip()
        headers.append(
            {
                "style": style,
                "text": text,
                "startIndex": element.get("startIndex"),
                "endIndex": element.get("endIndex"),
            }
        )
    return headers


def get_footnotes(doc_id: str) -> list[dict[str, str]]:
    """Read every footnote segment."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    return [
        {"footnote_id": footnote_id, "text": extract_text(footnote.get("content", []))}
        for footnote_id, footnote in document.get("footnotes", {}).items()
    ]


def read_table_data(doc_id: str) -> dict[str, Any]:
    """Extract all body tables into nested row/cell arrays."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    tables: list[list[list[str]]] = []
    for element in document_body(document):
        table = element.get("table")
        if not table:
            continue
        grid: list[list[str]] = []
        for row in table.get("tableRows", []):
            grid.append(
                [
                    extract_text(cell.get("content", [])).strip()
                    for cell in row.get("tableCells", [])
                ]
            )
        tables.append(grid)
    return {"tables": tables}


def read_links(doc_id: str) -> list[dict[str, Any]]:
    """Extract hyperlinks and their text ranges."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    links: list[dict[str, Any]] = []
    for paragraph_element, text_run in iter_text_runs(document_body(document)):
        link = text_run.get("textStyle", {}).get("link")
        if not link:
            continue
        links.append(
            {
                "text": text_run.get("content", "").strip(),
                "url": link.get("url"),
                "bookmarkId": link.get("bookmarkId"),
                "headingId": link.get("headingId"),
                "startIndex": paragraph_element.get("startIndex"),
                "endIndex": paragraph_element.get("endIndex"),
            }
        )
    return links


def create_comment(doc_id: str, text: str, context_text: str = "") -> dict[str, Any]:
    """Create a Drive comment; optional context is included in its content."""
    content = text
    if context_text:
        content = f"{text}\n\nContext: {context_text}"
    return execute(
        get_service("v3")
        .comments()
        .create(
            fileId=doc_id,
            body={"content": content},
            fields="id,content,createdTime,resolved",
        )
    )


def reply_to_comment(doc_id: str, comment_id: str, reply_text: str) -> dict[str, Any]:
    """Reply to an existing Drive comment."""
    return execute(
        get_service("v3")
        .replies()
        .create(
            fileId=doc_id,
            commentId=comment_id,
            body={"content": reply_text},
            fields="id,content,createdTime,modifiedTime",
        )
    )


def list_active_comments(doc_id: str) -> list[dict[str, Any]]:
    """List unresolved comments with their replies."""
    result = execute(
        get_service("v3")
        .comments()
        .list(
            fileId=doc_id,
            includeDeleted=False,
            fields=(
                "comments(id,author(displayName,emailAddress),content,createdTime,"
                "modifiedTime,resolved,quotedFileContent,replies(id,author,content,createdTime))"
            ),
        )
    )
    return [
        comment
        for comment in result.get("comments", [])
        if not comment.get("resolved", False)
    ]


def resolve_comment(doc_id: str, comment_id: str) -> dict[str, Any]:
    """Resolve a Drive comment by creating a resolve-action reply."""
    return execute(
        get_service("v3")
        .replies()
        .create(
            fileId=doc_id,
            commentId=comment_id,
            body={"action": "resolve"},
            fields="id,action,createdTime",
        )
    )


def insert_linked_bookmark(
    doc_id: str, index: int, bookmark_name: str
) -> dict[str, Any]:
    """Create a named range at an index as the API-supported bookmark analogue."""
    validate_index(index)
    if not bookmark_name.strip():
        raise ValueError("bookmark_name must not be empty.")
    response = execute(
        get_service("v1")
        .documents()
        .batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "createNamedRange": {
                            "name": bookmark_name,
                            "range": {"startIndex": index, "endIndex": index + 1},
                        }
                    }
                ]
            },
        )
    )
    named_range_id = None
    for reply in response.get("replies", []):
        named_range_id = reply.get("createNamedRange", {}).get("namedRangeId")
        if named_range_id:
            break
    return {
        "document_id": doc_id,
        "named_range_id": named_range_id,
        "name": bookmark_name,
        "note": "Google Docs API exposes named ranges, not editor bookmark creation.",
    }
