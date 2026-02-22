# ─────────────────────────────────────────────
# app/services/user_service.py
#
# PURPOSE: All user DB operations.
# Routes never query the DB directly — they call this.
# ─────────────────────────────────────────────

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from backend.app.models.models import User
from app.core.security import hash_password, verify_password


class UserService:

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_google_id(self, db: AsyncSession, google_id: str) -> User | None:
        result = await db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def create_email_user(
        self, db: AsyncSession, email: str, password: str, full_name: str | None = None
    ) -> User:
        """Register a new email/password user."""
        # Check email not already taken
        existing = await self.get_by_email(db, email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_verified=False,
        )
        db.add(user)
        await db.flush()   # get the generated ID without committing
        return user

    async def create_google_user(
        self, db: AsyncSession, google_id: str, email: str,
        full_name: str | None, avatar_url: str | None
    ) -> User:
        """Create a new user from Google OAuth data."""
        user = User(
            email=email,
            google_id=google_id,
            full_name=full_name,
            avatar_url=avatar_url,
            is_verified=True,   # Google already verified the email
        )
        db.add(user)
        await db.flush()
        return user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User:
        """Verify email + password. Returns user or raises 401."""
        user = await self.get_by_email(db, email)
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )
        return user


user_service = UserService()