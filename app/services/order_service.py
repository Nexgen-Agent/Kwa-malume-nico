from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Order, OrderItem, MenuItem, User
from app.schemas.schemas import OrderCreate
from datetime import datetime

def create_order(db: Session, order_data: OrderCreate, user_id: int = None):
    # Calculate total and delivery fee
    subtotal = 0.0
    items_to_create = []

    for item in order_data.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            continue

        item_price = menu_item.price
        subtotal += item_price * item.quantity

        items_to_create.append(OrderItem(
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price_at_time=item_price
        ))

    delivery_fee = 0.0
    if order_data.order_type == "delivery":
        delivery_fee = 30.0 if subtotal < 280.0 else 0.0

    total = subtotal + delivery_fee

    # Apply member discount if user_id exists
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.coupon_eligible:
            total = total * 0.9 # 10% discount

    db_order = Order(
        user_id=user_id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        order_type=order_data.order_type,
        address=order_data.address,
        instructions=order_data.instructions,
        table_number=order_data.table_number,
        total=total,
        delivery_fee=delivery_fee
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in items_to_create:
        item.order_id = db_order.id
        db.add(item)

    db.commit()
    db.refresh(db_order)
    return db_order

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

def get_all_orders(db: Session):
    return db.query(Order).order_by(Order.created_at.desc()).all()

def update_order_status(db: Session, order_id: int, status: str):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order:
        db_order.status = status

        # Update timestamps based on status
        now = datetime.now()
        if status == "preparing":
            db_order.accepted_at = now
        elif status == "ready":
            db_order.prepared_at = now
        elif status == "completed":
            db_order.delivered_at = now

        db.commit()
        db.refresh(db_order)
    return db_order

def assign_order_staff(db: Session, order_id: int, staff_id: int):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order:
        db_order.assigned_staff_id = staff_id
        db.commit()
        db.refresh(db_order)
    return db_order

def get_daily_sales(db: Session):
    # This is a simple implementation
    today = datetime.now().date()
    sales = db.query(
        func.sum(Order.total).label("total_sales"),
        func.count(Order.id).label("order_count")
    ).filter(func.date(Order.created_at) == today).first()

    return {
        "date": str(today),
        "total_sales": sales.total_sales or 0.0,
        "order_count": sales.order_count or 0
    }
