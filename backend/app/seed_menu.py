import asyncio
import logging
import os
import sys

# Add the parent directory to Python path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now use ABSOLUTE imports (not relative)
from app.db import engine, AsyncSessionLocal, Base
from app.models import MenuItem
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Menu items data
menu_items = [
    ("Titanic Family Kota", 100.0, "assets/img/menu/1.jpg"),
    ("Dunked Wings", 75.0, "assets/img/menu/2.jpg"),  # Fixed "Danked" to "Dunked"
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
        logger.info("✅ Database tables created successfully")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

async def seed_menu_items():
    """Seed menu items into the database"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if menu items already exist
            result = await session.execute(select(MenuItem))
            existing_items = result.scalars().all()

            if existing_items:
                logger.info(f"✅ Menu already seeded with {len(existing_items)} items")
                return True

            # Add new menu items
            for name, price, img_url in menu_items:
                menu_item = MenuItem(
                    name=name,
                    price=price,
                    img=img_url
                )
                session.add(menu_item)

            await session.commit()
            logger.info(f"✅ Successfully seeded {len(menu_items)} menu items")
            return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Database error seeding menu items: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def main():
    """Main function to run the seeding process"""
    logger.info("🚀 Starting database seeding process...")
    
    try:
        # Create tables
        if not await create_tables():
            return False
        
        # Seed data
        if not await seed_menu_items():
            return False
        
        logger.info("🎉 Seeding completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"💥 Seeding failed: {e}")
        return False

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    
    # Exit with appropriate code
    exit(0 if success else 1)