from pydantic import BaseModel, Field

PAK_PHONE_PATTERN = r"^(03\d{9}|\+923\d{9})$"

class OTPRequest(BaseModel):
    phone: str = Field(
        ...,
        pattern=PAK_PHONE_PATTERN,
        description="Pakistani mobile number: 03XXXXXXXXX or +923XXXXXXXXX"
    )

class OTPVerify(BaseModel):
    phone: str = Field(
        ...,
        pattern=PAK_PHONE_PATTERN
    )
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit numeric OTP"
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
