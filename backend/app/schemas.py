from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, date
from typing import List, Optional
from enum import Enum
import re

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

    model_config = {
        "from_attributes": True
    }

# ----- Orders -----
class OrderItemIn(BaseModel):
    menu_item_id: int = Field(..., gt=0)
    qty: int = Field(..., gt=0)

class OrderItemOut(OrderItemIn):
    id: int
    menu_item: MenuItemOut

    model_config = {
        "from_attributes": True
    }

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
    def validate_phone(cls, v):
        if v is not None:
            # Basic phone validation - remove non-digits and check length
            digits = re.sub(r'\D', '', v)
            if len(digits) < 7:  # Minimum phone number length
                raise ValueError('Invalid phone number format')
        return v

    @field_validator('table_number')
    @classmethod
    def validate_table_number(cls, v, info):
        if info.data.get('mode') == OrderMode.DINEIN and not v:
            raise ValueError('Table number is required for dine-in orders')
        return v

    model_config = {
        "use_enum_values": True
    }

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

    model_config = {
        "from_attributes": True
    }

# ----- Comments -----
class CommentIn(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=2000)

class CommentOut(CommentIn):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# ----- Bookings -----
class BookingIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    contact: str = Field(..., min_length=1, max_length=180)
    occasion: Optional[str] = Field(None, max_length=180)
    special_request: Optional[str] = Field("", max_length=1000)
    date: date
    time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')

    @field_validator('date')
    @classmethod
    def validate_date_not_in_past(cls, v):
        if v < date.today():
            raise ValueError('Booking date cannot be in the past')
        return v

class BookingOut(BookingIn):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# ----- Users -----
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    is_admin: bool = False

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# ----- Auth -----
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ----- Order Status -----
class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['pending', 'accepted', 'rejected', 'completed', 'preparing', 'ready']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v
