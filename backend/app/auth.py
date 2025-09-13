from datetime import datetime, timedelta
from typing import Optional
from authlib.jose import JWTError, jwt
from passlib.context import CryptContext
from litestar import Request
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from litestar.params import Dependency
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import get_async_session, AsyncSessionLocal
from .models import User
import os

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        {'alg': ALGORITHM},
        to_encode,
        SECRET_KEY
    )
    return encoded_jwt.decode('utf-8')

async def get_current_user(
    request: Request,
    session: AsyncSession = Dependency(get_async_session)
) -> User:
    """
    Dependency to get the current authenticated user from request headers.
    """
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise credentials_exception

        token = auth_header.split(" ")[1]

        # Use authlib's more robust decode method with key and algorithms
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: User = Dependency(get_current_user)) -> User:
    """
    Dependency to get the current authenticated admin user.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

async def get_current_user_from_token(token: str) -> Optional[User]:
    """
    Helper function to authenticate a user from a token,
    used specifically for WebSocket connections.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            return None

        # Create a new session specifically for this task
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            return result.scalar_one_or_none()

    except JWTError:
        return None
    except Exception as e:
        print(f"Error during token authentication: {e}")
        return None