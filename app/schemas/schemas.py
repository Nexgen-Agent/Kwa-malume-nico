from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    role: Optional[str] = None
    coupon_eligible: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    role: str
    coupon_eligible: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Menu Item Schemas
class MenuItemBase(BaseModel):
    name: str
    price: float
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# Order Schemas
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    price_at_time: float

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    customer_phone: str
    order_type: str
    address: Optional[str] = None
    instructions: Optional[str] = None
    table_number: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: int
    user_id: Optional[int]
    status: str
    total: float
    delivery_fee: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

# Admin / Stats Schemas
class DailySales(BaseModel):
    date: str
    total_sales: float
    order_count: int

# Review Schemas
class ReviewImageResponse(BaseModel):
    id: int
    image_url: str

    class Config:
        from_attributes = True

class ReviewCommentBase(BaseModel):
    text: str
    guest_name: Optional[str] = None

class ReviewCommentCreate(ReviewCommentBase):
    pass

class ReviewCommentResponse(ReviewCommentBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    full_name: Optional[str] = None # Helper field for UI

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    stars: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=1)
    guest_name: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False # For the current user
    images: List[ReviewImageResponse] = []
    comments: List[ReviewCommentResponse] = []
    full_name: Optional[str] = None # Helper field for UI

    class Config:
        from_attributes = True

class ReviewFeed(BaseModel):
    reviews: List[ReviewResponse]
    total_count: int
    page: int
    pages: int
