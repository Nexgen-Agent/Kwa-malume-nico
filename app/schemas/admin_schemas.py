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

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

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

class BudgetBase(BaseModel):
    month: int
    year: int
    category: str
    allocated_amount: float

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    month: Optional[int] = None
    year: Optional[int] = None
    category: Optional[str] = None
    allocated_amount: Optional[float] = None

class BudgetResponse(BudgetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_time: Optional[datetime] = None
    is_completed: Optional[bool] = False
    assigned_staff_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_time: Optional[datetime] = None
    is_completed: Optional[bool] = None
    assigned_staff_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    assigned_staff: Optional[StaffResponse] = None

    class Config:
        from_attributes = True

class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    progress_status: Optional[str] = "Not Started"
    assigned_staff_id: Optional[int] = None
    is_completed: Optional[bool] = False
    milestone_type: str # weekly, monthly, yearly

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    progress_status: Optional[str] = None
    assigned_staff_id: Optional[int] = None
    is_completed: Optional[bool] = None

class MilestoneResponse(MilestoneBase):
    id: int
    created_at: datetime
    assigned_staff: Optional[StaffResponse] = None

    class Config:
        from_attributes = True

class BudgetStatus(BaseModel):
    category: str
    allocated: float
    spent: float
    remaining: float

class DetailedFinanceReport(BaseModel):
    monthly_revenue: float
    monthly_expenses: float
    estimated_profit: float
    budgets: List[BudgetStatus]
    expense_logs: List[ExpenseResponse]
