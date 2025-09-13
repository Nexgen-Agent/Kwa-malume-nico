from litestar import Router, get
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_304_NOT_MODIFIED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.params import Dependency
from litestar.response import Response
from litestar.datastructures import Headers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import hashlib
from ..db import get_async_session
from ..models import MenuItem
from ..schemas import MenuItemOut
from litestar.response_headers import ResponseHeader, set_response_headers

# Create router - Litestar uses Router instead of APIRouter
router = Router(path="/menu", route_handlers=[])

def generate_etag(data: List[dict]) -> str:
    """
    Generate ETag for menu data.
    Uses a more efficient approach for larger datasets.
    """
    if not data:
        return hashlib.sha256(b"empty").hexdigest()

    # For efficiency, create a string of just the fields that affect the ETag
    # Ensure all values are converted to strings to prevent TypeErrors
    etag_data = "|".join(
        f"{item['id']}:{item['name']}:{item['price']}:{str(item.get('img', ''))}"
        for item in data
    )
    return hashlib.sha256(etag_data.encode()).hexdigest()

@get(
    "",
    response_model=List[MenuItemOut],
    # Use response_headers to set headers more idiomatically
    response_headers=[
        ResponseHeader(name="Cache-Control", value="public, max-age=86400, stale-while-revalidate=300"),
        ResponseHeader(name="Vary", value="Accept-Encoding")
    ]
)
async def list_menu(
    headers: Headers,
    db: AsyncSession = Dependency(get_async_session)
) -> List[MenuItemOut] | Response:
    """
    Lists all menu items and implements client-side caching with ETag.
    """
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
        if_none_match = headers.get("if-none-match")
        if if_none_match == etag:
            return Response(
                content=None,
                status_code=HTTP_304_NOT_MODIFIED
            )

        # Return response with caching headers
        set_response_headers(etag=etag)
        return menu_items

    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error fetching menu: {str(e)}"
        )

# Optional: Add endpoint for individual menu items
@get("/{item_id:int}", response_model=MenuItemOut)
async def get_menu_item(
    item_id: int, 
    db: AsyncSession = Dependency(get_async_session)
) -> MenuItemOut:
    """
    Retrieves a single menu item by ID.
    """
    try:
        result = await db.execute(
            select(MenuItem).where(MenuItem.id == item_id)
        )
        item = result.scalar_one_or_none()

        if item is None:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, 
                detail="Menu item not found"
            )

        return item

    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error fetching menu item: {str(e)}"
        )

# Register all routes with the router
router.register(list_menu)
router.register(get_menu_item)