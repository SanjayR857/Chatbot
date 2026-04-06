# ─────────────────────────────────────────────
# app/db/base.py
#
# PURPOSE: SQLAlchemy async engine + session setup.
#
# HOW IT WORKS:
#   create_engine → connects to PostgreSQL
#   AsyncSession  → every request gets its own
#                   session (transaction scope)
#   get_db()      → FastAPI dependency that
#                   provides a session and closes
#                   it when the request finishes
# ─────────────────────────────────────────────

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # objects stay usable after commit
)


# Base class all models inherit from
class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ─────────────────────────
# Used as: db: AsyncSession = Depends(get_db)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
