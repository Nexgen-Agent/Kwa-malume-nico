from datetime import datetime, timedelta
from typing import Optional
from authlib.jose import JWTError, jwt  # Changed from python-jose to authlib
from passlib.context import CryptContext
from litestar import Request
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from litestar.params import Dependency
from litestar.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_async_session
from .models import User
import os

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(token_url="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    # Authlib has slightly different API
    encoded_jwt = jwt.encode(
        {'alg': ALGORITHM},
        to_encode,
        SECRET_KEY
    )
    return encoded_jwt.decode('utf-8')  # Authlib returns bytes, decode to string

async def get_current_user(
    request: Request,  # Litestar passes request to dependencies
    session: AsyncSession = Dependency(get_async_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from request headers
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise credentials_exception
        
        token = auth_header.split(" ")[1]
        
        # Authlib JWT decoding
        payload = jwt.decode(token, SECRET_KEY)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # Get user from database
    from sqlalchemy import select
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: User = Dependency(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

# Litestar-compatible OAuth2 dependency
async def get_oauth2_token(request: Request) -> Optional[str]:
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None
