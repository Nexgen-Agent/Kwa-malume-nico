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
