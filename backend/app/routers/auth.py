from litestar import Router, post, get
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from litestar.params import Dependency
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_async_session
from .. import models, schemas
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user

# Create router - Litestar uses Router instead of APIRouter
router = Router(path="/auth", route_handlers=[])

@post("/register", response_model=schemas.UserOut)
async def register(
    user_data: schemas.UserCreate,
    session: AsyncSession = Dependency(get_async_session)
) -> schemas.UserOut:
    """
    Registers a new user and adds them to the database.
    """
    # Check if user with this username or email already exists
    result = await session.execute(
        select(models.User).where(
            (models.User.username == user_data.username) | 
            (models.User.email == user_data.email)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

@post("/token", response_model=schemas.Token)
async def login(
    data: schemas.UserCreate,
    session: AsyncSession = Dependency(get_async_session)
) -> schemas.Token:
    """
    Authenticates a user and returns a JWT access token.
    """
    result = await session.execute(
        select(models.User).where(models.User.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@get("/me", response_model=schemas.UserOut)
async def get_current_user_info(
    current_user: models.User = Dependency(get_current_user)
) -> schemas.UserOut:
    """
    Retrieves the information of the currently authenticated user.
    """
    return current_user

# Add routes to router (Litestar requires explicit registration)
router.register(register)
router.register(login) 
router.register(get_current_user_info)