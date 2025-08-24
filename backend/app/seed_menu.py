
import asyncio
from .db import engine, AsyncSessionLocal, Base
from .models import MenuItem
from sqlalchemy import select

items = [
 (1,"Titanic Family Kota",100,"assets/img/menu/1.jpg"),
 (2,"Danked Wings",75,"assets/img/menu/2.jpg"),
 (3,"Bugatti Kota",60,"assets/img/menu/3.jpg"),
 (4,"Burger",60,"assets/img/menu/4.jpg"),
 (5,"Range Rover Kota",50,"assets/img/menu/5.jpg"),
 (6,"Dagwood",45,"assets/img/menu/6.jpg"),
 (7,"BMW M4 Kota",40,"assets/img/menu/7.jpg"),
 (8,"Dessert",40,"assets/img/menu/8.jpg"),
 (9,"Omoda Kota",35,"assets/img/menu/9.jpg"),
 (10,"Haval Kota",30,"assets/img/menu/10.jpg"),
]

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as s:
        q = await s.execute(select(MenuItem))
        existing = q.scalars().all()
        if existing:
            print("Menu already seeded")
            return
        for (i,n,p,img) in items:
            s.add(MenuItem(id=i, name=n, price=p, img=img))
        await s.commit()
        print("Seeded menu items")

if __name__ == "__main__":
    asyncio.run(main())