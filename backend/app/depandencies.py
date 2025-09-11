from litestar.params import Parameter
from typing import Optional
from datetime import date

# Order filtering dependencies
async def order_filter_params(
    status: Optional[str] = Parameter(description="Filter by order status", default=None),
    start_date: Optional[date] = Parameter(description="Start date for filtering", default=None),
    end_date: Optional[date] = Parameter(description="End date for filtering", default=None),
    customer_name: Optional[str] = Parameter(description="Filter by customer name", default=None),
) -> dict:
    """Dependency for order filtering parameters."""
    return {
        "status": status,
        "start_date": start_date,
        "end_date": end_date,
        "customer_name": customer_name,
    }
