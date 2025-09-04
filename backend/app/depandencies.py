from fastapi import Depends, Query
from typing import Optional, List
from datetime import date
from . import filters

# Order filtering dependencies
async def order_filter_params(
    status: Optional[str] = Query(None, description="Filter by order status"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    customer_name: Optional[str] = Query(None, description="Filter by customer name"),
):
    return {
        "status": status,
        "start_date": start_date,
        "end_date": end_date,
        "customer_name": customer_name,
    }