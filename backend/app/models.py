from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Integer, String, Float, ForeignKey, DateTime, Text, func, Enum as SQLEnum, 
    Date, Time, Boolean  # ADDED Boolean import
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

# Enums for constrained values
class OrderMode(str, Enum):
    DINE_IN = "dinein"
    DELIVERY = "delivery"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

# ------------------------
# MENU (SINGLE DEFINITION)
# ------------------------
class MenuItem(Base):
    _tablename_ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    img: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())  # MOVED HERE

    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="menu_item")


# ------------------------
# ORDERS
# ------------------------
class Order(Base):
    _tablename_ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(255))
    mode: Mapped[OrderMode] = mapped_column(SQLEnum(OrderMode), default=OrderMode.DINE_IN)
    table_number: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="order", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class OrderItem(Base):
    _tablename_ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="order_items")


# ------------------------
# COMMENTS
# ------------------------
class Comment(Base):
    _tablename_ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ------------------------
# BOOKINGS
# ------------------------
class Booking(Base):
    _tablename_ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact: Mapped[str] = mapped_column(String(200), nullable=False)
    occasion: Mapped[str | None] = mapped_column(String(200))
    special_request: Mapped[str | None] = mapped_column(Text)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    time: Mapped[Time] = mapped_column(Time, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# ------------------------
# USERS
# ------------------------
class User(Base):
    _tablename_ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())