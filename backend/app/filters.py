from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from typing import Optional, Dict, Any
from . import models

async def filter_orders(
    session: AsyncSession,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 100
):
    """Filter orders based on provided criteria."""
    query = select(models.Order).order_by(models.Order.created_at.desc())

    conditions = []

    if filters.get("status"):
        conditions.append(models.Order.status == filters["status"])

    if filters.get("start_date"):
        start_datetime = datetime.combine(filters["start_date"], datetime.min.time())
        conditions.append(models.Order.created_at >= start_datetime)

    if filters.get("end_date"):
        end_datetime = datetime.combine(filters["end_date"], datetime.max.time())
        conditions.append(models.Order.created_at <= end_datetime)

    if filters.get("customer_name"):
        conditions.append(
            models.Order.customer_name.ilike(f"%{filters['customer_name']}%")
        )

    if conditions:
        query = query.where(and_(*conditions))

    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()
