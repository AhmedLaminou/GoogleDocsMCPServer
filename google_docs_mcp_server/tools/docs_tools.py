"""Document and Drive management tools."""

from __future__ import annotations

import base64
from typing import Any

from google_docs_mcp_server.tools.common import (
    document_body,
    document_end_index,
    escape_drive_query,
    execute,
    extract_text,
    get_service,
)

DOC_MIME_TYPE = "application/vnd.google-apps.document"
FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
PDF_MIME_TYPE = "application/pdf"
EXPORT_FORMATS = {
    "pdf": ("application/pdf", ".pdf"),
    "docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
    "odt": ("application/vnd.oasis.opendocument.text", ".odt"),
    "txt": ("text/plain", ".txt"),
    "html": ("application/zip", ".html.zip"),
    "epub": ("application/epub+zip", ".epub"),
    "rtf": ("application/rtf", ".rtf"),
}


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


def restore_doc(doc_id: str) -> dict[str, Any]:
    """Restore a document from Google Drive trash."""
    file = execute(
        get_service("v3")
        .files()
        .update(
            fileId=doc_id,
            body={"trashed": False},
            fields="id,name,trashed,webViewLink",
        )
    )
    return file


def rename_doc(doc_id: str, new_title: str) -> dict[str, Any]:
    """Rename a Google Doc in Drive."""
    title = new_title.strip()
    if not title:
        raise ValueError("new_title must not be empty.")
    return execute(
        get_service("v3")
        .files()
        .update(
            fileId=doc_id,
            body={"name": title},
            fields="id,name,modifiedTime,webViewLink",
        )
    )


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
    """Move a document exclusively into one Drive folder."""
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


def add_to_folder(doc_id: str, folder_id: str) -> dict[str, Any]:
    """Add a Drive folder as a parent without removing existing parents."""
    return execute(
        get_service("v3")
        .files()
        .update(
            fileId=doc_id,
            addParents=folder_id,
            fields="id,name,parents,webViewLink",
        )
    )


def remove_from_folder(doc_id: str, folder_id: str) -> dict[str, Any]:
    """Remove one parent folder from a document."""
    return execute(
        get_service("v3")
        .files()
        .update(
            fileId=doc_id,
            removeParents=folder_id,
            fields="id,name,parents,webViewLink",
        )
    )


def create_folder(name: str, parent_id: str = "") -> dict[str, Any]:
    """Create a Drive folder, optionally inside another folder."""
    folder_name = name.strip()
    if not folder_name:
        raise ValueError("name must not be empty.")
    body: dict[str, Any] = {"name": folder_name, "mimeType": FOLDER_MIME_TYPE}
    if parent_id.strip():
        body["parents"] = [parent_id.strip()]
    return execute(
        get_service("v3")
        .files()
        .create(body=body, fields="id,name,parents,webViewLink")
    )


def list_folders(query: str = "", limit: int = 20) -> list[dict[str, Any]]:
    """List folders visible to the active OAuth scope profile."""
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100.")
    drive_query = f"mimeType='{FOLDER_MIME_TYPE}' and trashed=false"
    if query.strip():
        drive_query += f" and name contains '{escape_drive_query(query.strip())}'"
    result = execute(
        get_service("v3")
        .files()
        .list(
            q=drive_query,
            orderBy="modifiedTime desc",
            pageSize=limit,
            fields="files(id,name,parents,modifiedTime,webViewLink)",
        )
    )
    return result.get("files", [])


def list_folder_contents(folder_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """List files and folders directly contained in a Drive folder."""
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000.")
    result = execute(
        get_service("v3")
        .files()
        .list(
            q=f"'{escape_drive_query(folder_id)}' in parents and trashed=false",
            orderBy="folder,name",
            pageSize=min(limit, 1000),
            fields="files(id,name,mimeType,modifiedTime,parents,webViewLink,size)",
        )
    )
    return result.get("files", [])


def export_doc(
    doc_id: str, output_format: str = "pdf", max_bytes: int = 10_000_000
) -> dict[str, Any]:
    """Export a Google Doc as a base64 payload in a supported format."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive.")
    selected = output_format.strip().lower()
    if selected not in EXPORT_FORMATS:
        raise ValueError(f"output_format must be one of {sorted(EXPORT_FORMATS)}.")
    mime_type, suffix = EXPORT_FORMATS[selected]
    service = get_service("v3")
    metadata = execute(service.files().get(fileId=doc_id, fields="name"))
    exported_bytes = execute(service.files().export(fileId=doc_id, mimeType=mime_type))
    if len(exported_bytes) > max_bytes:
        raise ValueError(
            f"Exported file is {len(exported_bytes)} bytes, exceeding max_bytes={max_bytes}."
        )
    return {
        "filename": f"{metadata.get('name', doc_id)}{suffix}",
        "format": selected,
        "mime_type": mime_type,
        "size_bytes": len(exported_bytes),
        "base64": base64.b64encode(exported_bytes).decode("ascii"),
    }


def export_to_pdf(doc_id: str, max_bytes: int = 10_000_000) -> dict[str, Any]:
    """Export a Google Doc as a base64-encoded PDF payload."""
    return export_doc(doc_id, "pdf", max_bytes)


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


def list_permissions(doc_id: str) -> list[dict[str, Any]]:
    """List Drive permissions on a document."""
    result = execute(
        get_service("v3")
        .permissions()
        .list(
            fileId=doc_id,
            fields=(
                "permissions(id,type,role,emailAddress,displayName,domain,"
                "allowFileDiscovery,expirationTime)"
            ),
        )
    )
    return result.get("permissions", [])


def update_permission(doc_id: str, permission_id: str, role: str) -> dict[str, Any]:
    """Change a user permission to reader, commenter, or writer."""
    if role not in {"reader", "commenter", "writer"}:
        raise ValueError("role must be reader, commenter, or writer.")
    return execute(
        get_service("v3")
        .permissions()
        .update(
            fileId=doc_id,
            permissionId=permission_id,
            body={"role": role},
            fields="id,type,role,emailAddress,displayName",
        )
    )


def list_revisions(doc_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """List available Drive revision metadata for a document."""
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000.")
    result = execute(
        get_service("v3")
        .revisions()
        .list(
            fileId=doc_id,
            pageSize=limit,
            fields=(
                "revisions(id,modifiedTime,keepForever,published,publishAuto,"
                "publishedOutsideDomain,lastModifyingUser(displayName,emailAddress))"
            ),
        )
    )
    return result.get("revisions", [])


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


def prepend_text(doc_id: str, text: str) -> dict[str, Any]:
    """Insert text at the beginning of the document body."""
    response = execute(
        get_service("v1")
        .documents()
        .batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {"insertText": {"location": {"index": 1}, "text": text}}
                ]
            },
        )
    )
    return {"document_id": doc_id, "prepended_characters": len(text), "response": response}


def replace_document_content(doc_id: str, text: str) -> dict[str, Any]:
    """Atomically replace all body text with new text."""
    service = get_service("v1")
    document = execute(service.documents().get(documentId=doc_id))
    end_index = document_end_index(document)
    requests: list[dict[str, Any]] = []
    if end_index > 1:
        requests.append(
            {
                "deleteContentRange": {
                    "range": {"startIndex": 1, "endIndex": end_index}
                }
            }
        )
    if text:
        requests.append({"insertText": {"location": {"index": 1}, "text": text}})
    if not requests:
        return {"document_id": doc_id, "replaced": False, "reason": "already empty"}
    response = execute(
        service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        )
    )
    return {
        "document_id": doc_id,
        "replaced": True,
        "inserted_characters": len(text),
        "response": response,
    }


def get_document_end_index(doc_id: str) -> dict[str, Any]:
    """Return the final writable body index for safe append/insert operations."""
    document = execute(get_service("v1").documents().get(documentId=doc_id))
    return {"document_id": doc_id, "end_index": document_end_index(document)}


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
