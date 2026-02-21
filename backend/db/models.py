# ─────────────────────────────────────────────
# app/db/models.py
#
# PURPOSE: SQLAlchemy ORM table definitions.
# Each class = one PostgreSQL table.
# SQLAlchemy maps Python objects ↔ DB rows.
# ─────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class User(Base):
    """
    Users table — stores both email/password
    and Google OAuth users in one table.

    email_password user: email + hashed_password set, google_id = NULL
    google user:         google_id set, hashed_password = NULL
    """
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    full_name       = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)   # NULL for Google users
    google_id       = Column(String, unique=True, nullable=True)  # NULL for email users
    avatar_url      = Column(String, nullable=True)   # Google profile picture
    is_active       = Column(Boolean, default=True)
    is_verified     = Column(Boolean, default=False)  # email verification flag

    # Timestamps (auto-set by DB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # One user → many chat messages
    messages = relationship("ChatMessage", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class ChatMessage(Base):
    """
    Stores all chat messages per user.
    Allows chat history to persist across sessions.
    """
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    role       = Column(String, nullable=False)    # "user" or "assistant"
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Many messages → one user
    user = relationship("User", back_populates="messages")