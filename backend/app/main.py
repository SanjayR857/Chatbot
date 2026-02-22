# ─────────────────────────────────────────────
# app/main.py
# Import path updated: app.db.database
# ─────────────────────────────────────────────

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router
from app.db.database import engine, Base            # ← updated: database not base
from app.models import models                       # ← import so SQLAlchemy sees the tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Auto-create all DB tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created/verified")
    yield
    await engine.dispose()
    print("🔌 Database connections closed")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="ChatterBot API — JWT OAuth2 Authentication",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    from app.api.routes.health import root
    app.get("/")(root)

    return app


app = create_app()