from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date
from .. import models, schemas, db, realtime
from ..auth import get_current_user, get_current_admin
from ..dependencies import order_filter_params
from ..filters import filter_orders

router = APIRouter(prefix="/orders", tags=["Orders"])

# Create order (no auth required for customers)
@router.post("/", response_model=schemas.OrderOut)
async def create_order(
    order_data: schemas.OrderCreate, 
    session: AsyncSession = Depends(db.get_async_session)
):
    # ... (your existing create_order implementation) ...
    pass

# Get orders with filtering (admin only)
@router.get("/", response_model=List[schemas.OrderOut])
async def get_orders(
    filters: dict = Depends(order_filter_params),
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db.get_async_session),
    current_user: models.User = Depends(get_current_admin)
):
    try:
        orders = await filter_orders(session, filters, skip, limit)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

# Get single order
@router.get("/{order_id}", response_model=schemas.OrderOut)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(db.get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    try:
        result = await session.execute(
            select(models.Order).where(models.Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        # Users can only see their own orders unless they're admin
        if not current_user.is_admin and order.customer_name != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
            
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order: {str(e)}")

# Update order status (admin only)
@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    session: AsyncSession = Depends(db.get_async_session),
    current_user: models.User = Depends(get_current_admin)
):
    try:
        result = await session.execute(
            select(models.Order).where(models.Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
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
        raise HTTPException(status_code=500, detail=f"Error updating order: {str(e)}")

# WebSocket with authentication
@router.websocket("/ws")
async def orders_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    # Authenticate WebSocket connection
    if not token:
        await websocket.close(code=4001)
        return
    
    try:
        # Verify token (simplified version)
        from ..auth import get_current_user
        # You'd need to adapt get_current_user for WebSocket
        # This is a simplified example
        user = await authenticate_websocket_token(token)
        
        if not user or not user.is_admin:
            await websocket.close(code=4003)
            return
            
        await websocket.accept()
        await realtime.order_manager.connect("orders", websocket)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Process messages if needed
                if data == "ping":
                    await websocket.send_text("pong")
                    
        except WebSocketDisconnect:
            realtime.order_manager.disconnect("orders", websocket)
            
    except Exception as e:
        try:
            await websocket.close()
        except:
            pass

async def authenticate_websocket_token(token: str):
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