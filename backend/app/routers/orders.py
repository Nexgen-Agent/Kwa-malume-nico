import asyncio
from litestar import Router, post, get, patch, websocket, WebSocket
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date, datetime
from .. import models, schemas, db, realtime
from ..auth import get_current_user, get_current_admin, get_current_user_from_token
from ..dependencies import order_filter_params
from ..filters import filter_orders

# Create router - Litestar uses Router instead of APIRouter
router = Router(path="/orders", route_handlers=[])

# Create order (no auth required for customers)
@post("/", response_model=schemas.OrderOut)
async def create_order(
    order_data: schemas.OrderCreate, 
    session: AsyncSession = Dependency(db.get_async_session)
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
@get("/", response_model=List[schemas.OrderOut])
async def get_orders(
    filters: dict = Dependency(order_filter_params),
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Dependency(db.get_async_session),
    current_user: models.User = Dependency(get_current_admin)
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
@get("/{order_id:int}", response_model=schemas.OrderOut)
async def get_order(
    order_id: int,
    session: AsyncSession = Dependency(db.get_async_session),
    current_user: models.User = Dependency(get_current_user)
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
@patch("/{order_id:int}/status", response_model=schemas.OrderOut)
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    session: AsyncSession = Dependency(db.get_async_session),
    current_user: models.User = Dependency(get_current_admin)
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