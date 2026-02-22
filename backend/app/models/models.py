# ─────────────────────────────────────────────
# app/models/models.py  (moved from app/db/models.py)
#
# PURPOSE: SQLAlchemy ORM table definitions.
# Import path updated:
#   from app.db.database import Base   ← not app.db.base
# ─────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base          # ← updated: database not base


class User(Base):
    """
    users table — email + password auth only.
    No Google OAuth fields.
    """
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    full_name       = Column(String(100), nullable=True)
    hashed_password = Column(String, nullable=False)      # bcrypt hash, never plain text
    is_active       = Column(Boolean, default=True,  nullable=False)
    is_verified     = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    messages = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete",
        lazy="select",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} active={self.is_active}>"


class ChatMessage(Base):
    """
    chat_messages table — one row per message.
    role = "user" or "assistant"
    """
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage id={self.id} user_id={self.user_id} role={self.role}>"