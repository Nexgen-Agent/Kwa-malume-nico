from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.schemas import OrderCreate, OrderResponse
from app.services import order_service
from app.auth.deps import get_current_user, get_current_active_user
from app.models.models import User
from typing import List, Optional

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/create", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user) # Optional for guest checkout
):
    user_id = current_user.id if current_user else None
    return order_service.create_order(db=db, order_data=order, user_id=user_id)

# Separate endpoint for actual guest checkout without even trying to get user
@router.post("/guest-create", response_model=OrderResponse)
def create_guest_order(order: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(db=db, order_data=order, user_id=None)

@router.get("/status/{order_id}", response_model=OrderResponse)
def get_order_status(order_id: int, db: Session = Depends(get_db)):
    db_order = order_service.get_order(db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/user", response_model=List[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return order_service.get_user_orders(db, user_id=current_user.id)
