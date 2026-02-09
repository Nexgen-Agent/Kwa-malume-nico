from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.schemas import OrderResponse, DailySales
from app.schemas.admin_schemas import (
    StaffCreate, StaffUpdate, StaffResponse,
    AttendanceCreate, AttendanceResponse,
    ExpenseCreate, ExpenseResponse,
    DashboardStats, GraphDataPoint, FinanceSummary
)
from app.services import order_service, admin_service
from app.auth.deps import check_role
from app.models.models import UserRole
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

# Dashboard Endpoints
@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.get_dashboard_stats(db)

@router.get("/dashboard/graph", response_model=List[GraphDataPoint])
def get_revenue_graph(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.get_revenue_graph_data(db)

# Order Management
@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin", "staff"]))
):
    return order_service.get_all_orders(db)

@router.patch("/orders/update/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin", "staff"]))
):
    db_order = order_service.update_order_status(db, order_id=order_id, status=status)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.patch("/orders/assign/{order_id}", response_model=OrderResponse)
def assign_order_staff(
    order_id: int,
    staff_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin", "staff"]))
):
    db_order = order_service.assign_order_staff(db, order_id=order_id, staff_id=staff_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# Staff Management
@router.get("/staff", response_model=List[StaffResponse])
def get_all_staff(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.get_all_staff(db)

@router.post("/staff", response_model=StaffResponse)
def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.create_staff(db, staff_data)

@router.patch("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    db_staff = admin_service.update_staff(db, staff_id, staff_data)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff

@router.delete("/staff/{staff_id}")
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    if not admin_service.delete_staff(db, staff_id):
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted successfully"}

# Attendance
@router.post("/attendance", response_model=AttendanceResponse)
def record_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.record_attendance(db, attendance_data.staff_id, attendance_data.status)

# Finance & Database
@router.get("/finance/summary", response_model=FinanceSummary)
def get_finance_summary(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.get_finance_summary(db)

@router.get("/finance/expenses", response_model=List[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.get_expenses(db)

@router.post("/finance/expenses", response_model=ExpenseResponse)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return admin_service.create_expense(db, expense_data)

# Legacy / Simple Stats
@router.get("/sales", response_model=DailySales)
def get_daily_sales(
    db: Session = Depends(get_db),
    admin: dict = Depends(check_role(["admin"]))
):
    return order_service.get_daily_sales(db)
