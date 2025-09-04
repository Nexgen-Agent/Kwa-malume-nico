# app/schemas.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import List, Optional, Dict, Any


# ----- Menu Items -----
class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    img: Optional[str]

    class Config:
        orm_mode = True


# ----- Orders -----
class OrderItemIn(BaseModel):
    menu_item_id: int
    qty: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    mode: str  # dinein or delivery
    customer_name: Optional[str] = None
    table_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    items: List[OrderItemIn]
    note: Optional[str] = ""

    @validator("mode")
    def validate_mode(cls, v):
        v = v.lower()
        if v not in ("dinein", "delivery"):
            raise ValueError("mode must be 'dinein' or 'delivery'")
        return v


class OrderOut(BaseModel):
    id: int
    customer_name: Optional[str]
    status: str
    total: float
    created_at: datetime

    class Config:
        orm_mode = True


# ----- Comments -----
class CommentIn(BaseModel):
    username: str = Field(..., max_length=120)
    message: str = Field(..., max_length=2000)


class CommentOut(CommentIn):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ----- Bookings -----
class BookingIn(BaseModel):
    name: str
    contact: str
    occasion: str
    special_request: Optional[str] = ""
    date: str  # could also use datetime.date if stricter validation wanted
    time: str  # could also use datetime.time

class BookingOut(BookingIn):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True