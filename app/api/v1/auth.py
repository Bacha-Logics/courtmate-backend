from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.schemas.user import OTPRequest, OTPVerify, TokenResponse
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.user import User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Request OTP
# -------------------------
@router.post("/request-otp")
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()

    if not user:
        user = User(phone=data.phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    otp = str(random.randint(100000, 999999))

    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)

    db.commit()

    # DEV ONLY (remove in production)
    return {
        "message": "OTP generated",
        "otp": otp
    }


# -------------------------
# Verify OTP + Login
# -------------------------
@router.post("/verify-otp")
def verify_otp_and_login(data: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()

    if not user or not user.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    # Clear OTP
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    # 🔥 INCLUDE ROLE IN TOKEN
    token = create_access_token(
        subject=str(user.id),
        extra_data={"is_admin": user.is_admin}
    )

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "is_admin": user.is_admin
        }
    }
