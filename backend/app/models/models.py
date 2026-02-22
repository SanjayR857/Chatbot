# ─────────────────────────────────────────────
# app/db/models.py
#
# PURPOSE: SQLAlchemy ORM table definitions.
# Each class = one PostgreSQL table.
# SQLAlchemy maps Python objects ↔ DB rows.
#
# Tables:
#   users         → registered accounts
#   chat_messages → all chat history per user
# ─────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base          # ← fixed import path (app.db.base not db.base)


# ─────────────────────────────────────────────
# USER TABLE
# ─────────────────────────────────────────────
class User(Base):
    """
    Stores email + password users ONLY.
    (Google OAuth removed — pure standard auth)

    Columns that were removed vs old version:
      ✗ google_id   — no Google OAuth
      ✗ avatar_url  — no Google profile picture

    hashed_password is now nullable=False
    because every user MUST have a password.
    """
    __tablename__ = "users"

    # ── Identity ──────────────────────────────
    id    = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # String(255) = max 255 chars — standard email length limit

    # ── Profile ───────────────────────────────
    full_name = Column(String(100), nullable=True)

    # ── Auth ──────────────────────────────────
    hashed_password = Column(String, nullable=False)
    # nullable=False → every user MUST have a password
    # stores bcrypt hash e.g. "$2b$12$..."
    # NEVER store plain text passwords

    # ── Status flags ──────────────────────────
    is_active   = Column(Boolean, default=True, nullable=False)
    # False = account disabled (soft delete — row stays in DB)

    is_verified = Column(Boolean, default=False, nullable=False)
    # False = email not verified yet
    # True  = user clicked verification link

    # ── Timestamps (auto-managed by PostgreSQL) ──
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),   # set by DB on INSERT
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),         # auto-updated by DB on every UPDATE
        nullable=True,               # NULL until first update
    )

    # ── Relationship ──────────────────────────
    # One user → many chat messages
    # cascade="all, delete" → deleting a user also
    # deletes all their messages automatically
    messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete",
        lazy="select",               # load messages only when accessed
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} active={self.is_active}>"


# ─────────────────────────────────────────────
# CHAT MESSAGE TABLE
# ─────────────────────────────────────────────
class ChatMessage(Base):
    """
    Stores every chat message (user + assistant).
    Linked to a user via foreign key.

    role = "user"      → message sent by the human
    role = "assistant" → reply from Ollama/LLM
    """
    __tablename__ = "chat_messages"

    # ── Identity ──────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    # ── Foreign Key ───────────────────────────
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,                  # index speeds up: "get all messages for user X"
    )
    # ondelete="CASCADE" → DB-level delete (backup to ORM cascade)

    # ── Message content ───────────────────────
    role = Column(
        String(20),
        nullable=False,
        # values: "user" or "assistant"
    )
    content = Column(
        Text,                        # Text = unlimited length (vs String which has limit)
        nullable=False,
    )

    # ── Timestamp ─────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationship ──────────────────────────
    # Many messages → one user
    user = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage id={self.id} user_id={self.user_id} role={self.role}>"