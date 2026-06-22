"""Document and Drive management tools."""

from __future__ import annotations

import base64
from typing import Any

from google_docs_mcp_server.tools.common import (
    document_body,
    escape_drive_query,
    execute,
    extract_text,
    get_service,
)

DOC_MIME_TYPE = "application/vnd.google-apps.document"
PDF_MIME_TYPE = "application/pdf"


def create_doc(title: str) -> dict[str, str]:
    """Create a blank Google Doc."""
    document = execute(
        get_service("v1").documents().create(body={"title": title})
    )
    return {
        "document_id": document["documentId"],
        "title": title,
        "url": f"https://docs.google.com/document/d/{document['documentId']}/edit",
    }


def delete_doc(doc_id: str) -> dict[str, Any]:
    """Move a document to Google Drive trash."""
    file = execute(
        get_service("v3")
        .files()
        .update(fileId=doc_id, body={"trashed": True}, fields="id, trashed")
    )
    return {"document_id": file.get("id", doc_id), "trashed": file.get("trashed", True)}


def copy_doc(doc_id: str, new_title: str) -> dict[str, str]:
    """Duplicate a Google Doc."""
    copied = execute(
        get_service("v3")
        .files()
        .copy(fileId=doc_id, body={"name": new_title}, fields="id, name, webViewLink")
    )
    return {
        "document_id": copied["id"],
        "title": copied.get("name", new_title),
        "url": copied.get(
            "webViewLink", f"https://docs.google.com/document/d/{copied['id']}/edit"
        ),
    }


def list_recent_docs(limit: int = 10) -> list[dict[str, str]]:
    """List recently modified Docs visible to the active OAuth scope profile."""
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100.")
    result = execute(
        get_service("v3")
        .files()
        .list(
            q=f"mimeType='{DOC_MIME_TYPE}' and trashed=false",
            orderBy="modifiedTime desc",
            pageSize=limit,
            fields="files(id, name, modifiedTime, webViewLink)",
        )
    )
    return result.get("files", [])


def search_docs(query: str, limit: int = 20) -> list[dict[str, str]]:
    """Search Docs visible to the active OAuth scope profile."""
    if not query.strip():
        raise ValueError("query must not be empty.")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100.")
    escaped = escape_drive_query(query.strip())
    drive_query = (
        f"mimeType='{DOC_MIME_TYPE}' and trashed=false and "
        f"(name contains '{escaped}' or fullText contains '{escaped}')"
    )
    result = execute(
        get_service("v3")
        .files()
        .list(
            q=drive_query,
            orderBy="modifiedTime desc",
            pageSize=limit,
            fields="files(id, name, modifiedTime, webViewLink)",
        )
    )
    return result.get("files", [])


def get_doc_metadata(doc_id: str) -> dict[str, Any]:
    """Return Drive metadata plus an approximate word count."""
    drive_file = execute(
        get_service("v3")
        .files()
        .get(
            fileId=doc_id,
            fields=(
                "id, name, owners(displayName,emailAddress), createdTime, modifiedTime, "
                "size, webViewLink, parents, trashed"
            ),
        )
    )
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    text = extract_text(document_body(document))
    drive_file["wordCount"] = len(text.split())
    drive_file["characterCount"] = len(text)
    return drive_file


def move_to_folder(doc_id: str, folder_id: str) -> dict[str, Any]:
    """Move a document into one Drive folder while preserving other parents."""
    service = get_service("v3")
    current = execute(service.files().get(fileId=doc_id, fields="parents"))
    previous_parents = ",".join(current.get("parents", []))
    kwargs = {
        "fileId": doc_id,
        "addParents": folder_id,
        "fields": "id, name, parents, webViewLink",
    }
    if previous_parents:
        kwargs["removeParents"] = previous_parents
    moved = execute(service.files().update(**kwargs))
    return moved


def export_to_pdf(doc_id: str, max_bytes: int = 10_000_000) -> dict[str, Any]:
    """Export a Google Doc as a base64-encoded PDF payload."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive.")
    service = get_service("v3")
    metadata = execute(service.files().get(fileId=doc_id, fields="name"))
    pdf_bytes = execute(service.files().export(fileId=doc_id, mimeType=PDF_MIME_TYPE))
    if len(pdf_bytes) > max_bytes:
        raise ValueError(
            f"Exported PDF is {len(pdf_bytes)} bytes, exceeding max_bytes={max_bytes}."
        )
    return {
        "filename": f"{metadata.get('name', doc_id)}.pdf",
        "mime_type": PDF_MIME_TYPE,
        "size_bytes": len(pdf_bytes),
        "base64": base64.b64encode(pdf_bytes).decode("ascii"),
    }


def share_doc(doc_id: str, email: str, role: str = "writer") -> dict[str, Any]:
    """Grant a user reader, commenter, or writer access."""
    if role not in {"reader", "commenter", "writer"}:
        raise ValueError("role must be reader, commenter, or writer.")
    return execute(
        get_service("v3")
        .permissions()
        .create(
            fileId=doc_id,
            body={"type": "user", "role": role, "emailAddress": email},
            sendNotificationEmail=True,
            fields="id, type, role, emailAddress",
        )
    )


def unshare_doc(doc_id: str, email: str) -> dict[str, Any]:
    """Remove all matching user permissions for an email address."""
    service = get_service("v3")
    result = execute(
        service.permissions().list(
            fileId=doc_id,
            fields="permissions(id,emailAddress,role,type)",
        )
    )
    matches = [
        permission
        for permission in result.get("permissions", [])
        if permission.get("emailAddress", "").casefold() == email.casefold()
    ]
    for permission in matches:
        execute(
            service.permissions().delete(
                fileId=doc_id, permissionId=permission["id"]
            )
        )
    return {"email": email, "removed_permission_ids": [p["id"] for p in matches]}


def read_full_doc(doc_id: str) -> str:
    """Read all body text, including text nested in tables."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    return extract_text(document_body(document))


def append_text(doc_id: str, text: str) -> dict[str, Any]:
    """Append text immediately before the document's final newline."""
    response = execute(
        get_service("v1")
        .documents()
        .batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "endOfSegmentLocation": {},
                            "text": text,
                        }
                    }
                ]
            },
        )
    )
    return {"document_id": doc_id, "appended_characters": len(text), "response": response}


def find_and_replace(
    doc_id: str, old_text: str, new_text: str, match_case: bool = False
) -> dict[str, Any]:
    """Replace all occurrences and return Google's replacement count."""
    response = execute(
        get_service("v1")
        .documents()
        .batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "replaceAllText": {
                            "containsText": {
                                "text": old_text,
                                "matchCase": match_case,
                            },
                            "replaceText": new_text,
                        }
                    }
                ]
            },
        )
    )
    occurrences = 0
    for reply in response.get("replies", []):
        occurrences += reply.get("replaceAllText", {}).get("occurrencesChanged", 0)
    return {"document_id": doc_id, "occurrences_changed": occurrences}
