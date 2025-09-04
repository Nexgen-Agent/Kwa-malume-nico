from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional

class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    img: Optional[str]

class OrderItemIn(BaseModel):
    menu_item_id: int
    qty: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    mode: str
    table_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    items: List[OrderItemIn]

    @validator("mode")
    def mode_check(cls, v):
        v = v.lower()
        if v not in ("dinein","delivery"):
            raise ValueError("mode must be 'dinein' or 'delivery'")
        return v

class OrderOut(BaseModel):
    id: int
    status: str
    total: float

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

# Comments
class CommentIn(BaseModel):
    name: str = Field(..., max_length=120)
    message: str = Field(..., max_length=2000)

class CommentOut(CommentIn):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Orders
class OrderIn(BaseModel):
    customer: str
    email: Optional[EmailStr] = None
    items: Dict[str, Any]
    note: Optional[str] = ""

class OrderOut(OrderIn):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Bookings
class BookingIn(BaseModel):
    name: str
    contact: str
    occasion: str
    special_request: Optional[str] = ""
    date: str
    time: str

class BookingOut(BookingIn):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

from pydantic import BaseModel
from datetime import datetime

# ----- Comments -----
class CommentBase(BaseModel):
    username: str
    message: str

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ----- Orders -----
class OrderBase(BaseModel):
    customer_name: str
    item: str

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True