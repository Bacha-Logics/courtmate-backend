import random
from datetime import datetime, timedelta

# TEMP storage (replace with Redis later)
_otp_store = {}

def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    _otp_store[phone] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }
    return otp

def verify_otp(phone: str, otp: str) -> bool:
    record = _otp_store.get(phone)
    if not record:
        return False
    if record["expires"] < datetime.utcnow():
        return False
    return record["otp"] == otp
