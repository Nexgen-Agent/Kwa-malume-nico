from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from .. import models, schemas, db, realtime

router = APIRouter(prefix="/orders", tags=["Orders"])

# Create order
@router.post("/", response_model=schemas.OrderOut)
# Make the function async
async def create_order(order: schemas.OrderCreate, session: Session = Depends(db.SessionLocal)):
    new_order = models.Order(**order.dict())
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    
    # Broadcast to all WebSocket clients
    # Now you can use await directly
    await realtime.order_manager.broadcast({
        "type": "order",
        "customer_name": new_order.customer_name,
        "item": new_order.item,
        "status": new_order.status,
        "created_at": str(new_order.created_at),
    })
    return new_order

# WebSocket for live orders
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await realtime.order_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        realtime.order_manager.disconnect(websocket)
