"""
This module contains dependency injection functions for API endpoints.

These functions are used to parse and validate request parameters
before they are passed to the route handlers.
"""
from typing import Optional
from datetime import date
from litestar import Request
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from litestar.params import Dependency
from app.models import User
from app.models import User
from app.database import get_async_session


# ----------------------------
# Order filtering dependencies
# ----------------------------
async def order_filter_params(
    status: Optional[str] = Parameter(description="Filter by order status", default=None),
    start_date: Optional[date] = Parameter(description="Start date for filtering", default=None),
    end_date: Optional[date] = Parameter(description="End date for filtering", default=None),
    customer_name: Optional[str] = Parameter(description="Filter by customer name", default=None),
) -> dict:
    """Dependency for order filtering parameters."""
    return {
        "status": status,
        "start_date": start_date,
        "end_date": end_date,
        "customer_name": customer_name,
    }


# ----------------------------
# Authentication dependencies
# ----------------------------

async def get_current_user(
    request: Request,
    session: AsyncSession = get_async_session()
) -> User:
    """
    Dependency to get the current authenticated user from the request headers.
    Replace token parsing logic with your JWT implementation.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token = auth_header.split(" ")[1]
    # TODO: Replace the following line with actual JWT decode to get username
    username = token

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_current_admin(current_user: User) -> User:
    """
    Dependency to ensure the current user is an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return current_user



async def get_admin_panel(current_user: User) -> dict:
    """
    Route handler for the admin panel.
    """
    return {"message": f"Welcome admin {current_user.username}"}