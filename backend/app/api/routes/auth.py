# ─────────────────────────────────────────────
# app/api/routes/auth.py
# Import path updated: app.models.models
#                      app.db.database
# ─────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db                  # ← updated
from app.models.models import User                  # ← updated
from app.schemes.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserResponse, ChangePasswordRequest,
    UpdateProfileRequest, MessageResponse,
)
from app.services.user_service import user_service
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Sign up with email + password. Auto-login after register."""
    user = await user_service.create(db, payload.email, payload.password, payload.full_name)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Sign in with email + password (JSON body)."""
    user = await user_service.authenticate(db, payload.email, payload.password)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/token", response_model=TokenResponse)
async def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 form login — used by Swagger UI Authorize button."""
    user = await user_service.authenticate(db, form.username, form.password)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange refresh token → new access + refresh tokens."""
    token_data = decode_token(payload.refresh_token)
    user = await user_service.get_by_id_or_404(db, int(token_data["sub"]))
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    payload: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update display name."""
    user = await user_service.update_profile(db, current_user, payload.full_name)
    return UserResponse.model_validate(user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password — requires current password verification."""
    await user_service.change_password(
        db, current_user, payload.current_password, payload.new_password
    )
    return MessageResponse(message="Password changed successfully")


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete account and all chat history."""
    await user_service.delete(db, current_user)
    return MessageResponse(message="Account permanently deleted")


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """Logout signal — frontend deletes token from localStorage."""
    return MessageResponse(message=f"Goodbye {current_user.email}! Delete your token on client.")