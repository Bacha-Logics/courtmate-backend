from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.client import ClientOut
from app.schemas.case import CaseOut
from app.services.client_service import get_clients, get_client_cases
from app.models.user import User

router = APIRouter(tags=["Clients"])


@router.get(
    "",
    response_model=List[ClientOut]
)
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_clients(db=db, current_user=current_user)


@router.get(
    "/{client_phone}/cases",
    response_model=List[CaseOut]
)
def get_cases_by_client(
    client_phone: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cases = get_client_cases(
        db=db,
        current_user=current_user,
        client_phone=client_phone
    )

    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cases found for this client"
        )

    return cases
