from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StaffBase(BaseModel):
    name: str
    role: str
    salary: float
    contact_info: Optional[str] = None
    employment_status: Optional[str] = "active"

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    salary: Optional[float] = None
    contact_info: Optional[str] = None
    employment_status: Optional[str] = None

class StaffResponse(StaffBase):
    id: int
    created_at: datetime
    days_worked: int = 0
    days_off: int = 0

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    staff_id: int
    status: str # present, off

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    category: str
    amount: float
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    monthly_revenue: float
    daily_revenue: float
    orders_count: int
    pending_orders: int
    completed_orders: int
    delivery_orders: int

class GraphDataPoint(BaseModel):
    date: str
    revenue: float

class FinanceSummary(BaseModel):
    total_income: float
    total_expenses: float
    estimated_profit: float
