# ─────────────────────────────────────────────
# app/models/auth.py — Pydantic schemas for Auth
#
# OAuth2PasswordRequestForm is FastAPI's built-in
# form handler for the standard OAuth2 flow.
# It expects: Content-Type: application/x-www-form-urlencoded
# with fields: username + password
# ─────────────────────────────────────────────

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ── Register ──────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Minimum 8 characters")
    full_name: Optional[str] = None


# ── Login (JSON body) ─────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Token response ────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# ── Refresh ───────────────────────────────────
class RefreshRequest(BaseModel):
    refresh_token: str


# ── Change Password ───────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


# ── Safe user shape (never expose hashed_password) ──
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True