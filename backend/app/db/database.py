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
from app.core.config import settings


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"

# Async engine — non-blocking DB calls for local PostgreSQL
engine = create_async_engine(
    f"{settings.DB_DRIVER}://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
    echo=True,             # logs SQL queries
    pool_size=10,          # max persistent connections
    max_overflow=20,       # extra connections allowed under load
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
