#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.insert(0, '/app')

async def seed_database():
    try:
        from app.database import engine, Base
        from app.models import MenuItem
        from app.database import AsyncSessionLocal
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Seed data
        menu_items = [
            ("Titanic Family Kota", 100.0, "assets/img/menu/1.jpg"),
            ("Dunked Wings", 75.0, "assets/img/menu/2.jpg"),
            # ... your other menu items
        ]
        
        async with AsyncSessionLocal() as session:
            for name, price, img in menu_items:
                item = MenuItem(name=name, price=price, img=img)
                session.add(item)
            await session.commit()
            
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Seeding failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(seed_database())