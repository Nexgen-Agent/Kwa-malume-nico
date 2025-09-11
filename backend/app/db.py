from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./malume.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True, 
    pool_pre_ping=True
)

# Async session maker (SQLAlchemy 2.0 style)
AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

# Base model class (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

# Async session dependency
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
