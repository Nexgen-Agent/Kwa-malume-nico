from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.schemas import OrderResponse, DailySales
from app.services import order_service
from app.auth.deps import check_role
from app.models.models import UserRole
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin", "staff"]))
):
    return order_service.get_all_orders(db)

@router.patch("/orders/update/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin", "staff"]))
):
    db_order = order_service.update_order_status(db, order_id=order_id, status=status)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/sales", response_model=DailySales)
def get_daily_sales(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return order_service.get_daily_sales(db)
