from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./backend/malume.db"

# create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

# async session maker
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


