from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
import os
import ssl

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./malume.db")

# For production PostgreSQL with SSL
if DATABASE_URL.startswith("postgresql+asyncpg"):
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
        pool_recycle=3600,
        connect_args={
            "ssl": ssl.create_default_context() if os.getenv("DB_SSL", "false").lower() == "true" else None
        }
    )
else:
    engine = create_async_engine(
        DATABASE_URL, 
        echo=False, 
        future=True, 
        pool_pre_ping=True
    )

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
