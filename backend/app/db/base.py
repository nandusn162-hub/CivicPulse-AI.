"""
backend/app/db/base.py
Database engine and session factory.
Supports both PostgreSQL (async) and SQLite (via aiosqlite).
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
from app.core.config import settings

# Determine the database URL and normalize for async drivers
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("sqlite:///") and not db_url.startswith("sqlite+"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)

# SQLite doesn't support pool_size / max_overflow
engine_kwargs = {"echo": settings.DEBUG}
if not db_url.startswith("sqlite"):
    engine_kwargs.update(pool_pre_ping=True, pool_size=10, max_overflow=20)

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Re-export the Base from models so Alembic and table creation can find it
from app.models.base import Base  # noqa: E402

# Enable WAL mode and foreign keys for SQLite
if db_url.startswith("sqlite"):
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def get_async_session():
    """FastAPI dependency — yields an async session and ensures cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Alias
get_db = get_async_session


async def create_tables():
    """Create all tables. Call once at startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
