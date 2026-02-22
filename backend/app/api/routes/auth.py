# ─────────────────────────────────────────────
# app/api/routes/auth.py
#
# Standard OAuth2 + JWT authentication routes:
#
#   POST /auth/register        → sign up
#   POST /auth/login           → sign in (returns JWT)
#   POST /auth/refresh         → get new access token
#   GET  /auth/me              → get current user profile
#   PUT  /auth/me              → update profile
#   POST /auth/change-password → change password
#   POST /auth/logout          → logout (client deletes token)
#
# Uses FastAPI's built-in OAuth2PasswordBearer
# which is the industry-standard OAuth2 flow.
# ─────────────────────────────────────────────

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm   # standard OAuth2 form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from backend.app.models.models import User
from app.schemes.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserResponse, ChangePasswordRequest,
)
from app.services.user_service import user_service
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── POST /auth/register ───────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Create a new account with email + password.
    Returns tokens immediately so user is auto-logged in.
    """
    user = await user_service.create(db, payload.email, payload.password, payload.full_name)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


# ── POST /auth/login (JSON) ───────────────────
@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Sign in with email + password (JSON body).
    Returns JWT access token + refresh token.
    """
    user = await user_service.authenticate(db, payload.email, payload.password)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


# ── POST /auth/token (OAuth2 standard form login) ──
@router.post("/token", response_model=TokenResponse)
async def login_oauth2_form(
    form: OAuth2PasswordRequestForm = Depends(),   # reads username + password from form data
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 standard login using form data.
    Used by Swagger UI's "Authorize" button.
    Field names are fixed by OAuth2 spec: 'username' and 'password'.
    We treat 'username' as email.
    """
    user = await user_service.authenticate(db, form.username, form.password)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


# ── POST /auth/refresh ────────────────────────
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    Call this when the frontend gets a 401 response.
    """
    token_data = decode_token(payload.refresh_token)
    user = await user_service.get_by_id(db, int(token_data["sub"]))
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


# ── GET /auth/me ──────────────────────────────
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently logged-in user's profile."""
    return UserResponse.model_validate(current_user)


# ── PUT /auth/me ──────────────────────────────
@router.put("/me", response_model=UserResponse)
async def update_profile(
    full_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the logged-in user's display name."""
    current_user.full_name = full_name
    return UserResponse.model_validate(current_user)


# ── POST /auth/change-password ────────────────
@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change password — requires the current password to be correct.
    Prevents attackers from changing password with a stolen access token.
    """
    await user_service.change_password(
        db, current_user, payload.current_password, payload.new_password
    )
    return {"message": "Password changed successfully"}


# ── POST /auth/logout ─────────────────────────
@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    JWT is stateless — tokens can't be server-side invalidated without a blocklist.
    The frontend deletes the token from localStorage on this signal.
    """
    return {"message": f"Goodbye {current_user.email}! Token deleted on client."}