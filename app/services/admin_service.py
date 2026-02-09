from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.models import Order, Staff, Attendance, Expense, OrderStatus
from app.schemas.admin_schemas import StaffCreate, StaffUpdate, ExpenseCreate
from datetime import datetime, timedelta

def get_dashboard_stats(db: Session):
    today = datetime.now().date()
    this_month = today.month
    this_year = today.year

    monthly_revenue = db.query(func.sum(Order.total)).filter(
        extract('month', Order.created_at) == this_month,
        extract('year', Order.created_at) == this_year,
        Order.status != OrderStatus.CANCELLED
    ).scalar() or 0.0

    daily_revenue = db.query(func.sum(Order.total)).filter(
        func.date(Order.created_at) == today,
        Order.status != OrderStatus.CANCELLED
    ).scalar() or 0.0

    orders_count = db.query(func.count(Order.id)).filter(
        func.date(Order.created_at) == today
    ).scalar() or 0

    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.PENDING
    ).scalar() or 0

    completed_orders = db.query(func.count(Order.id)).filter(
        Order.status == OrderStatus.COMPLETED
    ).scalar() or 0

    delivery_orders = db.query(func.count(Order.id)).filter(
        Order.order_type == "delivery",
        func.date(Order.created_at) == today
    ).scalar() or 0

    return {
        "monthly_revenue": monthly_revenue,
        "daily_revenue": daily_revenue,
        "orders_count": orders_count,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "delivery_orders": delivery_orders
    }

def get_revenue_graph_data(db: Session):
    today = datetime.now().date()
    # Get daily revenue for the last 30 days
    start_date = today - timedelta(days=30)

    results = db.query(
        func.date(Order.created_at).label("date"),
        func.sum(Order.total).label("revenue")
    ).filter(
        Order.created_at >= start_date,
        Order.status != OrderStatus.CANCELLED
    ).group_by(func.date(Order.created_at)).all()

    return [{"date": str(r.date), "revenue": r.revenue} for r in results]

# Staff Management
def create_staff(db: Session, staff_data: StaffCreate):
    db_staff = Staff(**staff_data.model_dump())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

def get_all_staff(db: Session):
    staff_list = db.query(Staff).all()
    # Add calculated fields for days worked/off
    for s in staff_list:
        s.days_worked = db.query(func.count(Attendance.id)).filter(
            Attendance.staff_id == s.id,
            Attendance.status == "present"
        ).scalar() or 0
        s.days_off = db.query(func.count(Attendance.id)).filter(
            Attendance.staff_id == s.id,
            Attendance.status == "off"
        ).scalar() or 0
    return staff_list

def update_staff(db: Session, staff_id: int, staff_data: StaffUpdate):
    db_staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not db_staff:
        return None

    update_data = staff_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_staff, key, value)

    db.commit()
    db.refresh(db_staff)
    return db_staff

def delete_staff(db: Session, staff_id: int):
    db_staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if db_staff:
        db.delete(db_staff)
        db.commit()
        return True
    return False

# Attendance
def record_attendance(db: Session, staff_id: int, status: str):
    today = datetime.now().date()
    # Check if already recorded for today
    existing = db.query(Attendance).filter(
        Attendance.staff_id == staff_id,
        func.date(Attendance.date) == today
    ).first()

    if existing:
        existing.status = status
    else:
        existing = Attendance(staff_id=staff_id, status=status)
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing

# Finances
def create_expense(db: Session, expense_data: ExpenseCreate):
    db_expense = Expense(**expense_data.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session):
    return db.query(Expense).order_by(Expense.date.desc()).all()

def get_finance_summary(db: Session):
    today = datetime.now().date()
    this_month = today.month
    this_year = today.year

    total_income = db.query(func.sum(Order.total)).filter(
        extract('month', Order.created_at) == this_month,
        extract('year', Order.created_at) == this_year,
        Order.status == OrderStatus.COMPLETED
    ).scalar() or 0.0

    total_expenses = db.query(func.sum(Expense.amount)).filter(
        extract('month', Expense.date) == this_month,
        extract('year', Expense.date) == this_year
    ).scalar() or 0.0

    # Also include salaries in expenses
    staff_salaries = db.query(func.sum(Staff.salary)).filter(Staff.employment_status == "active").scalar() or 0.0

    total_expenses += staff_salaries

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "estimated_profit": total_income - total_expenses
    }
