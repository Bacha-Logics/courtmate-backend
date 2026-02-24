import os
from typing import List
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.services.document_service import delete_document
from app.api.deps import get_db, get_current_user
from app.schemas.document import DocumentOut
from app.services.document_service import (
    upload_document,
    get_case_documents,
    get_document_for_download,
)
from app.models.user import User

router = APIRouter(tags=["Documents"])


# -------------------------
# Upload document
# -------------------------
@router.post(
    "",
    response_model=DocumentOut,
    status_code=status.HTTP_201_CREATED,
)
def upload_document_api(
    case_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        document = upload_document(
            db=db,
            file=file,
            case_id=case_id,
            current_user=current_user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    return document


# -------------------------
# List documents of a case
# -------------------------
@router.get(
    "/case/{case_id}",
    response_model=List[DocumentOut],
)
def list_case_documents_api(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = get_case_documents(
        db=db,
        case_id=case_id,
        current_user=current_user,
    )

    if documents is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    return documents


# -------------------------
# Download document
# -------------------------
@router.get(
    "/{document_id}/download",
)
def download_document_api(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_document_for_download(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = os.path.join("storage/documents", document.stored_name)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File missing on server",
        )

    return FileResponse(
        path=file_path,
        media_type=document.file_type,
        filename=document.original_name,
    )

# -------------------------
# Delete document
# -------------------------
@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_api(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = delete_document(
        db=db,
        document_id=document_id,
        current_user=current_user,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return