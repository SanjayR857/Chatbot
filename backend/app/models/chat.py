from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base          # ← updated: database not base



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