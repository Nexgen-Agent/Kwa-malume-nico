from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_async_session  # Use centralized dependency
from ..models import MenuItem
from ..schemas import MenuItemOut
import json
import hashlib
from typing import List

router = APIRouter(prefix="/menu", tags=["Menu"])

def generate_etag(data: List[dict]) -> str:
    """
    Generate ETag for menu data.
    Uses a more efficient approach for larger datasets.
    """
    if not data:
        return hashlib.sha256(b"empty").hexdigest()
    
    # For efficiency, create a string of just the fields that affect the ETag
    etag_data = "|".join(
        f"{item['id']}:{item['name']}:{item['price']}:{item.get('img', '')}"
        for item in data
    )
    return hashlib.sha256(etag_data.encode()).hexdigest()

@router.get("", response_model=List[MenuItemOut])
async def list_menu(
    request: Request, 
    response: Response, 
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # Fetch menu items from database
        result = await db.execute(select(MenuItem).order_by(MenuItem.id))
        menu_items = result.scalars().all()
        
        # Convert to list of dictionaries for ETag generation
        items_data = [
            {"id": item.id, "name": item.name, "price": item.price, "img": item.img}
            for item in menu_items
        ]
        
        # Generate ETag
        etag = generate_etag(items_data)
        
        # Check if client has current version
        if_none_match = request.headers.get("if-none-match")
        if if_none_match == etag:
            response.status_code = 304
            return None  # No body for 304 responses
        
        # Set caching headers
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=300"
        response.headers["Vary"] = "Accept-Encoding"  # Important for compressed responses
        
        return menu_items  # SQLAlchemy objects will be converted via response_model
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching menu: {str(e)}"
        )

# Optional: Add endpoint for individual menu items
@router.get("/{item_id}", response_model=MenuItemOut)
async def get_menu_item(
    item_id: int, 
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if item is None:
            raise HTTPException(status_code=404, detail="Menu item not found")
            
        return item
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching menu item: {str(e)}"
        )