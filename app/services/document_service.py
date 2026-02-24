import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.document import Document
from app.models.case import Case
from app.models.user import User


ALLOWED_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
UPLOAD_DIR = "storage/documents"


def upload_document(
    *,
    db: Session,
    file: UploadFile,
    case_id: int,
    current_user: User,
):
    # 1️⃣ Validate case ownership
    case = (
        db.query(Case)
        .filter(
            Case.id == case_id,
            Case.user_id == current_user.id
        )
        .first()
    )
    if not case:
        return None

    # 2️⃣ Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported file type")

    # 3️⃣ Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 4️⃣ Generate safe filename
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    # 5️⃣ Read & validate size
    contents = file.file.read()
    file.file.close()

    if len(contents) > MAX_FILE_SIZE:
        raise ValueError("File too large (max 10MB)")

    # 6️⃣ Save file to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    # 7️⃣ Save metadata in DB
    document = Document(
        original_name=file.filename,
        stored_name=stored_name,
        file_type=file.content_type,
        file_size=len(contents),
        uploaded_at=datetime.utcnow(),
        case_id=case.id,
        user_id=current_user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_case_documents(
    *,
    db: Session,
    case_id: int,
    current_user: User,
):
    case = (
        db.query(Case)
        .filter(
            Case.id == case_id,
            Case.user_id == current_user.id
        )
        .first()
    )

    if not case:
        return None

    return (
        db.query(Document)
        .filter(Document.case_id == case.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


def get_document_for_download(
    *,
    db: Session,
    document_id: int,
    current_user: User,
):
    return (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )

def delete_document(
    *,
    db: Session,
    document_id: int,
    current_user: User,
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        return None

    file_path = os.path.join(UPLOAD_DIR, document.stored_name)

    # Delete file from disk
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete DB record
    db.delete(document)
    db.commit()

    return True