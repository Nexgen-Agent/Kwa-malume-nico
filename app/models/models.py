from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.database import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class OrderType(str, enum.Enum):
    DINE_IN = "dine-in"
    PICKUP = "pickup"
    DELIVERY = "delivery"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default=UserRole.CUSTOMER)
    coupon_eligible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False) # chef, cashier, delivery, etc.
    salary = Column(Float, nullable=False)
    contact_info = Column(String)
    employment_status = Column(String, default="active") # active, inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    attendance = relationship("Attendance", back_populates="staff")
    orders = relationship("Order", back_populates="assigned_staff")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"))
    date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String) # present, off

    staff = relationship("Staff", back_populates="attendance")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    order_type = Column(String, nullable=False) # Enum values: dine-in, pickup, delivery
    status = Column(String, default=OrderStatus.PENDING)
    total = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    address = Column(String, nullable=True)
    instructions = Column(String, nullable=True)
    table_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    prepared_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    assigned_staff = relationship("Staff", back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_name = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    likes = relationship("ReviewLike", back_populates="review", cascade="all, delete-orphan")
    comments = relationship("ReviewComment", back_populates="review", cascade="all, delete-orphan")
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")

class ReviewLike(Base):
    __tablename__ = "review_likes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    review = relationship("Review", back_populates="likes")
    user = relationship("User")

class ReviewComment(Base):
    __tablename__ = "review_comments"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    guest_name = Column(String, nullable=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    review = relationship("Review", back_populates="comments")
    user = relationship("User")

class ReviewImage(Base):
    __tablename__ = "review_images"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    image_url = Column(String, nullable=False)

    review = relationship("Review", back_populates="images")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    allocated_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_time = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    assigned_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assigned_staff = relationship("Staff")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    deadline = Column(DateTime(timezone=True))
    progress_status = Column(String, default="Not Started") # Not Started, In Progress, Completed
    assigned_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    is_completed = Column(Boolean, default=False)
    milestone_type = Column(String, nullable=False) # weekly, monthly, yearly
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    assigned_staff = relationship("Staff")
