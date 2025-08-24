from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from ..db import AsyncSessionLocal
from ..models import MenuItem, Order, OrderItem
from ..schemas import OrderCreate, OrderOut
from ..realtime import broadcast
from typing import List

router = APIRouter(prefix="/api/orders", tags=["orders"])

FREE_DELIVERY_THRESHOLD = 280.0
DELIVERY_FEE = 25.0

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("", response_model=OrderOut)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    # validation
    if payload.mode == "dinein" and not payload.table_number:
        raise HTTPException(400, "Table number required for dine-in")
    if payload.mode == "delivery" and (not payload.phone or not payload.email):
        raise HTTPException(400, "Phone & email required for delivery")

    # compute totals
    sub = 0.0
    for it in payload.items:
        q = await db.execute(select(MenuItem).where(MenuItem.id == it.menu_item_id))
        mi = q.scalar_one_or_none()
        if not mi:
            raise HTTPException(404, f"Menu item {it.menu_item_id} not found")
        sub += mi.price * it.qty

    delivery = 0.0
    if payload.mode == "delivery" and sub < FREE_DELIVERY_THRESHOLD:
        delivery = DELIVERY_FEE
    grand_total = sub + delivery

    # insert order
    res = await db.execute(insert(Order).values(
        mode=payload.mode,
        table_number=payload.table_number,
        phone=payload.phone,
        email=payload.email,
        status="pending",
        total=grand_total
    ))
    await db.commit()
    order_id = int(res.inserted_primary_key[0])

    # insert order items
    for it in payload.items:
        await db.execute(insert(OrderItem).values(
            order_id=order_id, menu_item_id=it.menu_item_id, qty=it.qty
        ))
    await db.commit()

    # decide room: table:<num> for dinein, order:<id> for delivery
    room = f"table:{payload.table_number}" if payload.mode == "dinein" else f"order:{order_id}"
    await broadcast(room, {"type":"order:new","orderId":order_id,"total":grand_total})

    return {"id": order_id, "status": "pending", "total": grand_total}