# ─────────────────────────────────────────────
# app/utils/dependencies.py
#
# Uses OAuth2PasswordBearer — the FastAPI standard
# for OAuth2 token auth. Points to /auth/token so
# Swagger UI knows where to get a token from.
# ─────────────────────────────────────────────

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from backend.app.models.models import User
from app.core.security import decode_token
from app.services.user_service import user_service

# Tells FastAPI where the login endpoint is (for Swagger UI)
# Automatically extracts Bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Auth guard — add to any route:
        current_user: User = Depends(get_current_user)

    Steps:
      1. Extract JWT from Authorization: Bearer <token>
      2. Decode & verify signature + expiry
      3. Look up user in DB
      4. Return user object (or raise 401/403)
    """
    payload = decode_token(token)       # raises 401 if invalid/expired

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    return user