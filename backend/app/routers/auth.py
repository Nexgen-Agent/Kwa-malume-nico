from datetime import datetime, timedelta
from typing import Optional

from litestar import Router, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from authlib.jose import jwt
from passlib.context import CryptContext

from ..database import get_async_session
from .. import models, schemas

import os

# =============================
# 🔐 JWT CONFIG
# =============================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =============================
# 🔑 PASSWORD HASHING
# =============================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode({"alg": ALGORITHM}, to_encode, SECRET_KEY)
    return token.decode("utf-8") if isinstance(token, bytes) else token


# =============================
# 🧩 DEPENDENCY HELPERS
# =============================
async def get_current_user(request, session: AsyncSession = Provide(get_async_session)) -> models.User:
    """Extract and validate JWT from Authorization header."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY)
        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid token payload")
    except Exception:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    result = await session.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_current_admin(current_user: models.User = Provide(get_current_user)) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


# =============================
# 🚀 ROUTES
# =============================
@post("/register", summary="Register a new user", tags=["Auth"])
async def register(
    user_data: schemas.UserCreate,
    session: AsyncSession = Provide(get_async_session),
) -> schemas.UserOut:
    """Registers a new user and stores them in the DB."""
    existing = await session.execute(
        select(models.User).where(
            (models.User.username == user_data.username)
            | (models.User.email == user_data.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Username or email already exists")

    user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_admin=getattr(user_data, "is_admin", False),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@post("/token", summary="Login and get access token", tags=["Auth"])
async def login(
    credentials: schemas.UserCreate,
    session: AsyncSession = Provide(get_async_session),
) -> schemas.Token:
    """Authenticate a user and return a JWT token."""
    result = await session.execute(select(models.User).where(models.User.username == credentials.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@get("/me", summary="Get current user info", tags=["Auth"])
async def me(current_user: models.User = Provide(get_current_user)) -> schemas.UserOut:
    """Retrieve info for the currently logged-in user."""
    return current_user


@get("/admin", summary="Get current admin info", tags=["Auth"])
async def admin_info(current_user: models.User = Provide(get_current_admin)) -> schemas.UserOut:
    """Retrieve info for the currently logged-in admin."""
    return current_user


# =============================
# 🧭 ROUTER EXPORT
# =============================
router = Router(
    path="/auth",
    route_handlers=[register, login, me, admin_info],
    dependencies={"session": Provide(get_async_session)},
)