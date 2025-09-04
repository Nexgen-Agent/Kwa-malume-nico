from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .. import models, schemas, db, realtime

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=schemas.OrderOut)
async def create_order(
    order_data: schemas.OrderCreate, 
    session: AsyncSession = Depends(db.get_async_session)
):
    try:
        # Calculate total from order items
        total = 0.0
        order_items = []
        
        # Validate menu items exist and calculate total
        for item_in in order_data.items:
            # Get menu item from database
            result = await session.execute(
                select(models.MenuItem).where(models.MenuItem.id == item_in.menu_item_id)
            )
            menu_item = result.scalar_one_or_none()
            
            if not menu_item:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Menu item with ID {item_in.menu_item_id} not found"
                )
            
            # Calculate item total
            item_total = menu_item.price * item_in.qty
            total += item_total
            
            # Create order item
            order_item = models.OrderItem(
                menu_item_id=item_in.menu_item_id,
                qty=item_in.qty
            )
            order_items.append(order_item)
        
        # Create order
        new_order = models.Order(
            customer_name=order_data.customer_name,
            phone=order_data.phone,
            email=order_data.email,
            mode=order_data.mode,
            table_number=order_data.table_number,
            note=order_data.note,
            total=total,
            items=order_items
        )
        
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        
        # Get complete order with items for broadcast
        await session.refresh(new_order, ['items'])
        for item in new_order.items:
            await session.refresh(item, ['menu_item'])
        
        # Broadcast to all WebSocket clients
        await realtime.order_manager.broadcast(
            "orders",  # Room name
            "new_order",  # Event type
            {
                "id": new_order.id,
                "customer_name": new_order.customer_name,
                "mode": new_order.mode,
                "status": new_order.status,
                "total": float(new_order.total),
                "created_at": new_order.created_at.isoformat(),
                "items": [
                    {
                        "menu_item_name": item.menu_item.name,
                        "quantity": item.qty,
                        "price": float(item.menu_item.price)
                    }
                    for item in new_order.items
                ]
            }
        )
        
        return new_order
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@router.get("/", response_model=List[schemas.OrderOut])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(db.get_async_session)
):
    try:
        result = await session.execute(
            select(models.Order)
            .order_by(models.Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = result.scalars().all()
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

@router.get("/{order_id}", response_model=schemas.OrderOut)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(db.get_async_session)
):
    try:
        result = await session.execute(
            select(models.Order).where(models.Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
            
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order: {str(e)}")

# WebSocket for live orders
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection first
    await websocket.accept()
    
    # Connect to the order manager
    await realtime.order_manager.connect("orders", websocket)
    
    try:
        while True:
            # Keep connection alive and process messages
            data = await websocket.receive_text()
            
            # Optional: process incoming messages
            # For example, admin could update order status via WebSocket
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        # Handle disconnection
        realtime.order_manager.disconnect("orders", websocket)
    except Exception as e:
        # Handle other errors
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
        realtime.order_manager.disconnect("orders", websocket)