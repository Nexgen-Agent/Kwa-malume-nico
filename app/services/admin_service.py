from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.models import Order, Staff, Attendance, Expense, OrderStatus, Budget, Task, Milestone
from app.schemas.admin_schemas import (
    StaffCreate, StaffUpdate, ExpenseCreate, ExpenseUpdate,
    BudgetCreate, BudgetUpdate, TaskCreate, TaskUpdate,
    MilestoneCreate, MilestoneUpdate
)
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

def update_expense(db: Session, expense_id: int, expense_data: ExpenseUpdate):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense: return None
    for key, value in expense_data.model_dump(exclude_unset=True).items():
        setattr(db_expense, key, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
        return True
    return False

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

# Budget Management
def create_budget(db: Session, budget_data: BudgetCreate):
    db_budget = Budget(**budget_data.model_dump())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, budget_data: BudgetUpdate):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget: return None
    for key, value in budget_data.model_dump(exclude_unset=True).items():
        setattr(db_budget, key, value)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int):
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if db_budget:
        db.delete(db_budget)
        db.commit()
        return True
    return False

def get_detailed_finance_report(db: Session):
    today = datetime.now().date()
    month = today.month
    year = today.year

    summary = get_finance_summary(db)

    # Get budgets for this month
    budgets = db.query(Budget).filter(Budget.month == month, Budget.year == year).all()
    budget_statuses = []

    for b in budgets:
        spent = db.query(func.sum(Expense.amount)).filter(
            Expense.category == b.category,
            extract('month', Expense.date) == month,
            extract('year', Expense.date) == year
        ).scalar() or 0.0

        budget_statuses.append({
            "category": b.category,
            "allocated": b.allocated_amount,
            "spent": spent,
            "remaining": b.allocated_amount - spent
        })

    expenses = get_expenses(db)

    return {
        "monthly_revenue": summary["total_income"],
        "monthly_expenses": summary["total_expenses"],
        "estimated_profit": summary["estimated_profit"],
        "budgets": budget_statuses,
        "expense_logs": expenses
    }

# Task Management
def create_task(db: Session, task_data: TaskCreate):
    db_task = Task(**task_data.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(db: Session):
    return db.query(Task).order_by(Task.due_time.asc()).all()

def update_task(db: Session, task_id: int, task_data: TaskUpdate):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task: return None
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

# Milestone Management
def create_milestone(db: Session, milestone_data: MilestoneCreate):
    db_milestone = Milestone(**milestone_data.model_dump())
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

def get_milestones(db: Session, milestone_type: str = None):
    query = db.query(Milestone)
    if milestone_type:
        query = query.filter(Milestone.milestone_type == milestone_type)
    return query.order_by(Milestone.deadline.asc()).all()

def update_milestone(db: Session, milestone_id: int, milestone_data: MilestoneUpdate):
    db_milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not db_milestone: return None
    for key, value in milestone_data.model_dump(exclude_unset=True).items():
        setattr(db_milestone, key, value)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

def delete_milestone(db: Session, milestone_id: int):
    db_milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if db_milestone:
        db.delete(db_milestone)
        db.commit()
        return True
    return False
