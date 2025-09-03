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

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json, asyncio
from .. import models, schemas
from ..db import get_db
from ..realtime import hub

router = APIRouter(prefix="/orders", tags=["Orders & Reviews"])

# Comments
@router.post("/comments", response_model=schemas.CommentOut)
def create_comment(body: schemas.CommentIn, db: Session = Depends(get_db)):
    row = models.Comment(name=body.name, message=body.message)
    db.add(row); db.commit(); db.refresh(row)
    asyncio.create_task(hub.broadcast("comment_created", schemas.CommentOut.from_orm(row).dict()))
    return row

@router.get("/comments", response_model=list[schemas.CommentOut])
def list_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).order_by(models.Comment.created_at.desc()).all()

# Orders
@router.post("/", response_model=schemas.OrderOut)
def create_order(body: schemas.OrderIn, db: Session = Depends(get_db)):
    row = models.Order(customer=body.customer, email=body.email,
                       items=json.dumps(body.items), note=body.note or "")
    db.add(row); db.commit(); db.refresh(row)
    data = schemas.OrderOut(id=row.id, customer=row.customer,
                            email=row.email, items=body.items,
                            note=row.note, created_at=row.created_at)
    asyncio.create_task(hub.broadcast("order_created", data.dict()))
    return data

@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    rows = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [
        schemas.OrderOut(
            id=r.id, customer=r.customer, email=r.email,
            items=json.loads(r.items or "{}"), note=r.note, created_at=r.created_at
        )
        for r in rows
    ]

# Bookings
@router.post("/bookings", response_model=schemas.BookingOut)
def create_booking(body: schemas.BookingIn, db: Session = Depends(get_db)):
    row = models.Booking(**body.dict())
    db.add(row); db.commit(); db.refresh(row)
    data = schemas.BookingOut.from_orm(row)
    asyncio.create_task(hub.broadcast("booking_created", data.dict()))
    return data

@router.get("/bookings", response_model=list[schemas.BookingOut])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).order_by(models.Booking.created_at.desc()).all()