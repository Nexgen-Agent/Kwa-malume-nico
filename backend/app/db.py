from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./malume.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

# Async session maker (SQLAlchemy 1.4 compatible)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(declarative_base()):
    pass

# Async session dependency
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()