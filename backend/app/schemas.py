from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from enum import Enum
import re

# For Pydantic v2 compatibility
try:
    from pydantic import ConfigDict
    PYDANTIC_V2 = True
except ImportError:
    PYDANTIC_V2 = False


# ----- Enums -----
class OrderMode(str, Enum):
    DINEIN = "dinein"
    DELIVERY = "delivery"


# ----- Menu Items -----
class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    img: Optional[str] = None

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


# ----- Orders -----
class OrderItemIn(BaseModel):
    menu_item_id: int = Field(..., gt=0)
    qty: int = Field(..., gt=0)


class OrderItemOut(OrderItemIn):
    id: int
    menu_item: MenuItemOut

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class OrderCreate(BaseModel):
    mode: OrderMode
    customer_name: str = Field(..., min_length=1, max_length=120)
    table_number: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    items: List[OrderItemIn] = Field(..., min_items=1)
    note: Optional[str] = Field("", max_length=500)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v, values):
        if v is not None:
            # Basic phone validation - remove non-digits and check length
            digits = re.sub(r'\D', '', v)
            if len(digits) < 7:  # Minimum phone number length
                raise ValueError('Invalid phone number format')
        return v

    @field_validator('table_number')
    @classmethod
    def validate_table_number(cls, v, values):
        if values.data.get('mode') == OrderMode.DINEIN and not v:
            raise ValueError('Table number is required for dine-in orders')
        return v

    if PYDANTIC_V2:
        model_config = ConfigDict(use_enum_values=True)
    else:
        @validator("mode", pre=True)
        def validate_mode(cls, v):
            if isinstance(v, str):
                v = v.lower()
            if v not in [mode.value for mode in OrderMode]:
                raise ValueError(f"Mode must be one of: {[mode.value for mode in OrderMode]}")
            return v


class OrderOut(BaseModel):
    id: int
    customer_name: str
    phone: Optional[str]
    email: Optional[str]
    mode: str
    table_number: Optional[str]
    status: str
    total: float
    note: Optional[str]
    created_at: datetime
    items: List[OrderItemOut]

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


# ----- Comments -----
class CommentIn(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=2000)


class CommentOut(CommentIn):
    id: int
    created_at: datetime

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


# ----- Bookings -----
class BookingIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    contact: str = Field(..., min_length=1, max_length=180)
    occasion: Optional[str] = Field(None, max_length=180)
    special_request: Optional[str] = Field("", max_length=1000)
    date: date  # Use proper date type
    time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')  # HH:MM format

    @field_validator('date')
    @classmethod
    def validate_date_not_in_past(cls, v):
        if v < date.today():
            raise ValueError('Booking date cannot be in the past')
        return v


class BookingOut(BookingIn):
    id: int
    created_at: datetime

    if PYDANTIC_V2:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True