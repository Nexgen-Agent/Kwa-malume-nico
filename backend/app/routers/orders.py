from litestar import Router, post, get, patch, websocket, WebSocket
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date, datetime
from .. import models, schemas, db, realtime
from ..auth import get_current_user, get_current_admin
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
    # ... (your existing create_order implementation) ...
    pass

# Get orders with filtering (admin only)
@get("/", response_model=List[schemas.OrderOut])
async def get_orders(
    filters: dict = Dependency(order_filter_params),
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Dependency(db.get_async_session),
    current_user: models.User = Dependency(get_current_admin)
) -> List[schemas.OrderOut]:
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
    # Authenticate WebSocket connection
    if not token:
        await websocket.close(code=4001)
        return

    try:
        # Verify token (simplified version)
        user = await authenticate_websocket_token(token)

        if not user or not user.is_admin:
            await websocket.close(code=4003)
            return

        await websocket.accept()
        await realtime.order_manager.connect("orders", websocket)

        try:
            while True:
                data = await websocket.receive_data()
                # Process messages if needed
                if data == "ping":
                    await websocket.send_data("pong")

        except Exception:
            realtime.order_manager.disconnect("orders", websocket)

    except Exception as e:
        try:
            await websocket.close()
        except:
            pass
        realtime.order_manager.disconnect("orders", websocket)

async def authenticate_websocket_token(token: str) -> Optional[models.User]:
    # Simplified WebSocket authentication
    # In production, use proper JWT validation
    from ..auth import jwt, SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        # Get user from database
        async with db.AsyncSessionLocal() as session:
            result = await session.execute(
                select(models.User).where(models.User.username == username)
            )
            return result.scalar_one_or_none()
    except Exception:
        return None

# Register all routes with the router
router.register(create_order)
router.register(get_orders)
router.register(get_order)
router.register(update_order_status)
router.register(orders_websocket)
