import asyncio
from litestar import Router, post, get, patch, websocket, WebSocket
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date, datetime
from .. import models, schemas, database, realtime
from ..auth import get_current_user, get_current_admin, get_current_user_from_token
from ..depandencies import order_filter_params
from ..filters import filter_orders
from ..database import get_async_session
from app.depandencies import get_current_admin
from app.depandencies import get_admin_panel
from app.models import User

# Create router - Litestar uses Router instead of APIRouter
router = Router(path="/orders", route_handlers=[])

# Create order (no auth required for customers)
@post("/", response_model=schemas.OrderOut, dependencies={"session": get_async_session})
async def create_order(
    order_data: schemas.OrderCreate,
    session: AsyncSession
) -> schemas.OrderOut:
    """
    Creates a new order from customer data.
    """
    try:
        new_order = models.Order(**order_data.model_dump())
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)

        return new_order
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}"
        )

# Get orders with filtering (admin only)
@get("/", response_model=List[schemas.OrderOut], dependencies={
    "session": get_async_session,
    "filters": order_filter_params,
    "current_user": get_current_admin  # admin-only
})
async def get_orders(
    filters: dict,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = None,
    current_user: models.User = None
) -> List[schemas.OrderOut]:
    """
    Retrieves a filtered and paginated list of orders (admin only).
    """
    try:
        orders = await filter_orders(session, filters, skip, limit)
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error fetching orders: {str(e)}"
        )

# Get single order
@get("/{order_id:int}", response_model=schemas.OrderOut, dependencies={
    "session": get_async_session,
    "current_user": get_current_user
})
async def get_order(
    order_id: int,
    session: AsyncSession,
    current_user: models.User
) -> schemas.OrderOut:
    """
    Retrieves a single order by ID.
    Users can only view their own orders unless they are an admin.
    """
    try:
        result = await session.execute(
            select(models.Order).where(models.Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, 
                detail="Order not found"
            )

        # Users can only see their own orders unless they're admin
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="Not authorized to view this order"
            )

        return order
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error fetching order: {str(e)}"
        )

# Update order status (admin only)
@patch("/{order_id:int}/status", response_model=schemas.OrderOut, dependencies={
    "session": get_async_session,
    "current_user": get_current_admin
})
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    session: AsyncSession,
    current_user: models.User
) -> schemas.OrderOut:
    """
    Updates the status of an order (admin only).
    """
    try:
        result = await session.execute(
            select(models.Order).where(models.Order.id == order_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, 
                detail="Order not found"
            )

        order.status = status_update.status
        await session.commit()
        await session.refresh(order)

        # Broadcast status update
        await realtime.order_manager.broadcast(
            "orders",
            "status_update",
            {
                "order_id": order.id,
                "status": order.status,
                "updated_at": datetime.utcnow().isoformat()
            }
        )

        return order
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error updating order: {str(e)}"
        )

# WebSocket with authentication
@websocket("/ws")
async def orders_websocket(
    websocket: WebSocket,
    token: Optional[str] = Parameter(query="token", default=None)
) -> None:
    """
    Real-time WebSocket connection for order updates (admin only).
    """
    await websocket.accept()

    if not token:
        await websocket.close(code=4001, reason="Authentication token missing")
        return

    try:
        user = await get_current_user_from_token(token)

        if not user or not user.is_admin:
            await websocket.close(code=4003, reason="Forbidden")
            return

        await realtime.order_manager.connect("orders", websocket)

        try:
            # Keep the connection open indefinitely
            async for _ in websocket.iter_bytes():
                pass
        finally:
            realtime.order_manager.disconnect("orders", websocket)

    except Exception as e:
        print(f"WebSocket error: {e}")
        realtime.order_manager.disconnect("orders", websocket)
        try:
            await websocket.close()
        except:
            pass