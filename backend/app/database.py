from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from dotenv import load_dotenv
import os
import ssl

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./malume.db")

# For production PostgreSQL with SSL
if DATABASE_URL.startswith("postgresql+asyncpg"):
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
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
        pool_pre_ping=True
    )

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
