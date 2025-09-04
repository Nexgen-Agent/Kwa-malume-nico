import asyncio
import logging
from .db import engine, AsyncSessionLocal, Base
from .models import MenuItem
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Menu items data - without IDs (let database handle auto-increment)
menu_items = [
    ("Titanic Family Kota", 100.0, "assets/img/menu/1.jpg"),
    ("Danked Wings", 75.0, "assets/img/menu/2.jpg"),
    ("Bugatti Kota", 60.0, "assets/img/menu/3.jpg"),
    ("Burger", 60.0, "assets/img/menu/4.jpg"),
    ("Range Rover Kota", 50.0, "assets/img/menu/5.jpg"),
    ("Dagwood", 45.0, "assets/img/menu/6.jpg"),
    ("BMW M4 Kota", 40.0, "assets/img/menu/7.jpg"),
    ("Dessert", 40.0, "assets/img/menu/8.jpg"),
    ("Omoda Kota", 35.0, "assets/img/menu/9.jpg"),
    ("Haval Kota", 30.0, "assets/img/menu/10.jpg"),
]

async def create_tables():
    """Create database tables if they don't exist"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        raise

async def seed_menu_items():
    """Seed menu items into the database"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if menu items already exist
            result = await session.execute(select(MenuItem))
            existing_items = result.scalars().all()
            
            if existing_items:
                logger.info(f"Menu already seeded with {len(existing_items)} items")
                return
            
            # Add new menu items
            for name, price, img_url in menu_items:
                menu_item = MenuItem(
                    name=name,
                    price=price,
                    img=img_url
                )
                session.add(menu_item)
            
            await session.commit()
            logger.info(f"Successfully seeded {len(menu_items)} menu items")
            
    except SQLAlchemyError as e:
        logger.error(f"Error seeding menu items: {e}")
        await session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await session.rollback()
        raise

async def main():
    """Main function to run the seeding process"""
    try:
        await create_tables()
        await seed_menu_items()
        logger.info("Seeding completed successfully")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        # Exit with error code
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())