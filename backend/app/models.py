from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, func, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

class MenuItem(Base):
    __tablename__ = "menu_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    img: Mapped[str] = mapped_column(String(255), nullable=True)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)  # dinein | delivery
    table_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    total: Mapped[float] = mapped_column(Float, default=0)
    created_at = Column(DateTime, server_default=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .db import Base

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer = Column(String(120))
    email = Column(String(180))
    items = Column(Text)  # JSON string
    note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    contact = Column(String(180))
    occasion = Column(String(180))
    special_request = Column(Text, default="")
    date = Column(String(32))
    time = Column(String(32))
    created_at = Column(DateTime, default=datetime.utcnow)