from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, Dict, Any
from . import models

async def filter_orders(
    session: AsyncSession,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 100
):
    """
    Filters orders based on provided criteria.

    Args:
        session: The SQLAlchemy AsyncSession for database interaction.
        filters: A dictionary of filter criteria (e.g., status, start_date, end_date).
        skip: The number of records to skip for pagination.
        limit: The maximum number of records to return.

    Returns:
        A list of filtered Order objects.
    """
    query = select(models.Order).order_by(models.Order.created_at.desc())

    conditions = []

    # Filter by status
    if filters.get("status"):
        conditions.append(models.Order.status == filters["status"])

    # Filter by date range
    if filters.get("start_date"):
        start_datetime = datetime.combine(filters["start_date"], datetime.min.time())
        conditions.append(models.Order.created_at >= start_datetime)

    if filters.get("end_date"):
        end_datetime = datetime.combine(filters["end_date"], datetime.max.time())
        conditions.append(models.Order.created_at <= end_datetime)

    # Filter by customer name
    if filters.get("customer_name"):
        conditions.append(
            models.Order.customer_name.ilike(f"%{filters['customer_name']}%")
        )

    # Apply all conditions to the query
    if conditions:
        query = query.where(and_(*conditions))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()