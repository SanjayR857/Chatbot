# ─────────────────────────────────────────────
# app/services/user_service.py
#
# PURPOSE: All user-related database operations.
# Routes never query the DB directly — they call
# methods on this service.
#
# Methods:
#   get_by_id        → fetch user by primary key
#   get_by_email     → fetch user by email
#   create           → register new user
#   authenticate     → verify email + password
#   update_profile   → change full_name
#   change_password  → verify old → set new
#   deactivate       → soft-delete (is_active=False)
#   delete           → hard-delete from DB
# ─────────────────────────────────────────────

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from app.models.models import User, ChatMessage
from app.core.security import hash_password, verify_password


class UserService:

    # ─────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────

    async def get_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        """
        Fetch a single user by their primary key ID.
        Returns None if not found (caller decides how to handle).
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """
        Fetch a single user by email address.
        Email is stored lowercase — compare case-insensitively.
        Returns None if not found.
        """
        result = await db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_404(self, db: AsyncSession, user_id: int) -> User:
        """
        Fetch user by ID — raises 404 if not found.
        Use this when the user MUST exist (e.g. admin routes).
        """
        user = await self.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id={user_id} not found",
            )
        return user

    # ─────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────

    async def create(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> User:
        """
        Register a brand new user.

        Steps:
          1. Normalize email (lowercase + strip)
          2. Check email not already taken → 409
          3. Hash the password (never store plain text)
          4. Insert into DB via flush() to get ID
             without committing (commit happens in get_db)

        Raises:
          409 Conflict → email already registered
        """
        # 1. Normalize email
        email = email.lower().strip()

        # 2. Check uniqueness
        existing = await self.get_by_email(db, email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        # 3. Create user object
        user = User(
            email=email,
            hashed_password=hash_password(password),  # bcrypt hash
            full_name=full_name.strip() if full_name else None,
            is_active=True,
            is_verified=False,  # set True after email verification
        )

        # 4. Persist
        db.add(user)
        await db.flush()   # writes to DB in current transaction, gets auto-generated id
        await db.refresh(user)  # reload from DB to get created_at etc.
        return user

    # ─────────────────────────────────────────
    # AUTHENTICATE
    # ─────────────────────────────────────────

    async def authenticate(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        """
        Verify email + password for login.

        Security note: we return the SAME error message
        whether email doesn't exist OR password is wrong.
        This prevents user enumeration attacks
        (attacker can't tell if an email is registered).

        Raises:
          401 Unauthorized → wrong email or password
          403 Forbidden    → account disabled
        """
        user = await self.get_by_email(db, email)

        # Deliberate: same message for "no user" and "wrong password"
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been disabled. Contact support.",
            )

        return user

    # ─────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────

    async def update_profile(
        self,
        db: AsyncSession,
        user: User,
        full_name: str,
    ) -> User:
        """
        Update the user's display name.
        The user object is already loaded (from get_current_user),
        so we just mutate it — SQLAlchemy tracks the change.
        Commit happens automatically in get_db().
        """
        user.full_name = full_name.strip()
        await db.flush()
        await db.refresh(user)
        return user

    async def change_password(
        self,
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:
        """
        Change user's password.

        Steps:
          1. Verify current password is correct → 400 if wrong
          2. Hash new password
          3. Save (commit via get_db)

        Raises:
          400 Bad Request → current password is wrong
        """
        # 1. Verify current
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # 2. Hash + save new password
        user.hashed_password = hash_password(new_password)
        await db.flush()
        return user

    async def verify_email(self, db: AsyncSession, user: User) -> User:
        """
        Mark a user's email as verified.
        Call this after the user clicks the verification link.
        """
        user.is_verified = True
        await db.flush()
        return user

    # ─────────────────────────────────────────
    # DELETE / DEACTIVATE
    # ─────────────────────────────────────────

    async def deactivate(self, db: AsyncSession, user: User) -> User:
        """
        Soft delete — sets is_active=False.
        User row stays in DB (preserves chat history, audit trail).
        Deactivated users cannot login (authenticate() raises 403).
        """
        user.is_active = False
        await db.flush()
        return user

    async def delete(self, db: AsyncSession, user: User) -> None:
        """
        Hard delete — permanently removes user + all their messages.
        cascade="all, delete" on the relationship handles messages.
        Only use this for GDPR deletion requests or admin cleanup.
        """
        await db.delete(user)
        await db.flush()

    async def clear_chat_history(self, db: AsyncSession, user_id: int) -> int:
        """
        Delete all chat messages for a user.
        Returns the number of messages deleted.
        """
        result = await db.execute(
            delete(ChatMessage).where(ChatMessage.user_id == user_id)
        )
        await db.flush()
        return result.rowcount   # number of rows deleted


# ─────────────────────────────────────────────
# Singleton instance
# Import this everywhere:
#   from app.services.user_service import user_service
# ─────────────────────────────────────────────
user_service = UserService()