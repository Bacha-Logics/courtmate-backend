from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.case import CaseCreate, CaseUpdate, CaseOut
from app.services import case_service
from app.models.user import User


router = APIRouter(tags=["Cases"])



# -------------------------
# Create a new case
# -------------------------
@router.post(
    "",
    response_model=CaseOut,
    status_code=status.HTTP_201_CREATED
)
def create_case(
    case_in: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return case_service.create_case(
        db=db,
        case_in=case_in,
        current_user=current_user
    )


# -------------------------
# Get all cases of current user
# -------------------------
@router.get(
    "",
    response_model=List[CaseOut]
)
def list_my_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return case_service.get_user_cases(
        db=db,
        current_user=current_user
    )


# -------------------------
# Get single case by ID
# -------------------------
@router.get(
    "/{case_id}",
    response_model=CaseOut
)
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_case = case_service.get_case_by_id(
        db=db,
        case_id=case_id,
        current_user=current_user
    )

    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    return db_case


# -------------------------
# Update a case
# -------------------------
@router.put(
    "/{case_id}",
    response_model=CaseOut
)
def update_case(
    case_id: int,
    case_in: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_case = case_service.get_case_by_id(
        db=db,
        case_id=case_id,
        current_user=current_user
    )

    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    return case_service.update_case(
        db=db,
        db_case=db_case,
        case_in=case_in
    )


# -------------------------
# Delete a case
# -------------------------
@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_case = case_service.get_case_by_id(
        db=db,
        case_id=case_id,
        current_user=current_user
    )

    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    case_service.delete_case(
        db=db,
        db_case=db_case
    )



from app.schemas.case_detail import CaseDetailOut


@router.get(
    "/{case_id}/detail",
    response_model=CaseDetailOut,
    status_code=status.HTTP_200_OK
)
def get_case_detail_api(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = case_service.get_case_detail(
        db=db,
        case_id=case_id,
        current_user=current_user
    )

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )

    return data

