from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import AsyncSessionLocal
from ..models import MenuItem
from ..schemas import MenuItemOut
import json, hashlib

router = APIRouter(prefix="/api/menu", tags=["menu"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def make_etag(obj):
    raw = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()

@router.get("", response_model=list[MenuItemOut])
async def list_menu(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(MenuItem))
    items = [ {"id":m.id, "name":m.name, "price":m.price, "img":m.img} for m in res.scalars().all() ]
    etag = make_etag(items)
    if request.headers.get("if-none-match") == etag:
        response.status_code = 304
        return []
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=300"
    return items