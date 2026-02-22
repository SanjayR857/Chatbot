# ─────────────────────────────────────────────
# app/models/auth.py
#
# Pydantic v2 schemas for standard OAuth2
# (email + password, JWT, no Google OAuth).
#
# FLOW:
#   Register  → RegisterRequest  → TokenResponse
#   Login     → LoginRequest     → TokenResponse
#   Refresh   → RefreshRequest   → TokenResponse
#   Me        →                  → UserResponse
#   Change PW → ChangePasswordRequest → MessageResponse
#   Logout    →                  → MessageResponse
# ─────────────────────────────────────────────

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
import re


# ─────────────────────────────────────────────
# 1. RegisterRequest
#    Used by: POST /auth/register
# ─────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr                                    # validates email format automatically
    password: str = Field(
        min_length=8,
        max_length=128,   # safe — we SHA-256 prehash before bcrypt (no 72-byte issue)
        description="8–128 chars, must contain letter + number",
    )
    confirm_password: str = Field(min_length=8, max_length=128)        # must match password
    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    # ── Validator 1: password strength ────────
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Enforces:
          - At least one letter
          - At least one digit
        You can add more rules here (special chars etc.)
        """
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

    # ── Validator 2: passwords match ──────────
    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        """
        model_validator runs AFTER all field_validators.
        Checks confirm_password == password.
        """
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    # ── Validator 3: clean full_name ──────────
    @field_validator("full_name", mode="before")
    @classmethod
    def strip_name(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from full_name if provided."""
        return v.strip() if v else v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "password": "Secret123",
                "confirm_password": "Secret123",
                "full_name": "John Doe",
            }
        }
    }


# ─────────────────────────────────────────────
# 2. LoginRequest
#    Used by: POST /auth/login  (JSON body)
#    Note: POST /auth/token uses OAuth2PasswordRequestForm
#          (form data, not JSON — handled by FastAPI)
# ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john@example.com",
                "password": "Secret123",
            }
        }
    }


# ─────────────────────────────────────────────
# 3. UserResponse
#    Returned inside TokenResponse and GET /auth/me
#    NEVER include hashed_password here.
# ─────────────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool

    # from_attributes=True lets Pydantic read from
    # SQLAlchemy model objects directly:
    #   UserResponse.model_validate(user_db_object)
    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# 4. TokenResponse
#    Returned after: register, login, token refresh
#    Contains both access + refresh tokens + user info
# ─────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str                  # short-lived  (default: 60 min)
    refresh_token: str                 # long-lived   (default: 7 days)
    token_type: str = "bearer"         # OAuth2 standard — always "bearer"
    user: UserResponse                 # so frontend doesn't need a 2nd request

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_verified": False,
                },
            }
        }
    }


# ─────────────────────────────────────────────
# 5. RefreshRequest
#    Used by: POST /auth/refresh
#    Frontend sends this when access token expires (401)
# ─────────────────────────────────────────────
class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiJ9..."}
        }
    }


# ─────────────────────────────────────────────
# 6. ChangePasswordRequest
#    Used by: POST /auth/change-password
#    Requires current password to prevent misuse
#    of stolen access tokens
# ─────────────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(
        min_length=8,
        max_length=128,   # safe — SHA-256 prehash before bcrypt
    )
    confirm_new_password: str = Field(min_length=8, max_length=128)

    # ── Validator 1: new password strength ────
    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("New password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("New password must contain at least one number")
        return v

    # ── Validator 2: new passwords match ──────
    @model_validator(mode="after")
    def new_passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match")
        return self

    # ── Validator 3: new != current ───────────
    @model_validator(mode="after")
    def new_differs_from_current(self) -> "ChangePasswordRequest":
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from current password")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "OldPass1",
                "new_password": "NewPass2",
                "confirm_new_password": "NewPass2",
            }
        }
    }


# ─────────────────────────────────────────────
# 7. UpdateProfileRequest
#    Used by: PUT /auth/me
# ─────────────────────────────────────────────
class UpdateProfileRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {"full_name": "Jane Doe"}
        }
    }


# ─────────────────────────────────────────────
# 8. MessageResponse
#    Generic success message for logout,
#    change-password, etc.
# ─────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {"message": "Operation successful"}
        }
    }