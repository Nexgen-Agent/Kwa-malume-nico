from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_async_session
from .. import models, schemas
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserOut)
async def register(
    user_data: schemas.UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    # Check if user exists
    result = await session.execute(
        select(models.User).where(
            (models.User.username == user_data.username) | 
            (models.User.email == user_data.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    
    # Create new user
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

@router.post("/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(models.User).where(models.User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    return current_user