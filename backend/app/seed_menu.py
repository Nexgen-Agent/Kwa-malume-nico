"""
BULLETPROOF DATABASE SEEDER FOR MALUME NICO
This version handles all possible errors and dependencies
"""

import os
import sys
import asyncio
import logging
<<<<<<< HEAD
=======
import os
import sys

# Add the parent directory to Python path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now use ABSOLUTE imports (not relative)
from app.db import engine, AsyncSessionLocal, Base
from app.models import MenuItem
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
>>>>>>> 765fdbc334cbad664aa5db1b05a3a1177f21a0c3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
<<<<<<< HEAD
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_required_packages():
    """Install required packages if missing"""
    required_packages = [
        'sqlalchemy',
        'aiosqlite',
        'asyncpg'
    ]
    
    for package in required_packages:
        try:
            _import_(package)
            logger.info(f"✅ {package} is already installed")
        except ImportError:
            logger.warning(f"⚠ Installing missing package: {package}")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✅ Successfully installed {package}")
            except Exception as e:
                logger.error(f"❌ Failed to install {package}: {e}")
                return False
    return True
=======
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
>>>>>>> 765fdbc334cbad664aa5db1b05a3a1177f21a0c3

def setup_database():
    """Setup database connection and models without complex imports"""
    try:
        # Install packages first
        if not install_required_packages():
            return False
        
        # Now import (after ensuring packages are installed)
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import String, Float, Integer
        
        # Define Base model locally to avoid import issues
        class Base(DeclarativeBase):
            pass
        
        # Define MenuItem model locally
        class MenuItem(Base):
            _tablename_ = "menu_items"
            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(200), nullable=False)
            price: Mapped[float] = mapped_column(Float, nullable=False)
            img: Mapped[str] = mapped_column(String(500), nullable=True)
        
        # Menu items data
        menu_items = [
            ("Titanic Family Kota", 100.0, "assets/img/menu/1.jpg"),
            ("Dunked Wings", 75.0, "assets/img/menu/2.jpg"),
            ("Bugatti Kota", 60.0, "assets/img/menu/3.jpg"),
            ("Burger", 60.0, "assets/img/menu/4.jpg"),
            ("Range Rover Kota", 50.0, "assets/img/menu/5.jpg"),
            ("Dagwood", 45.0, "assets/img/menu/6.jpg"),
            ("BMW M4 Kota", 40.0, "assets/img/menu/7.jpg"),
            ("Dessert", 40.0, "assets/img/menu/8.jpg"),
            ("Omoda Kota", 35.0, "assets/img/menu/9.jpg"),
            ("Haval Kota", 30.0, "assets/img/menu/10.jpg"),
        ]
        
        # Database setup
        database_url = "sqlite+aiosqlite:///./malume.db"
        engine = create_async_engine(database_url, echo=True)
        AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
        
        return engine, AsyncSessionLocal, Base, MenuItem, menu_items
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return None

async def create_tables(engine, Base):
    """Create database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
        return True
<<<<<<< HEAD
    except Exception as e:
=======
    except SQLAlchemyError as e:
>>>>>>> 765fdbc334cbad664aa5db1b05a3a1177f21a0c3
        logger.error(f"❌ Error creating tables: {e}")
        return False

async def seed_menu_items(AsyncSessionLocal, MenuItem, menu_items):
    """Seed menu items into the database"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if menu items already exist
            from sqlalchemy import select
            result = await session.execute(select(MenuItem))
            existing_items = result.scalars().all()

            if existing_items:
                logger.info(f"✅ Menu already seeded with {len(existing_items)} items")
                return True

            # Add new menu items
            for name, price, img_url in menu_items:
                menu_item = MenuItem(name=name, price=price, img=img_url)
                session.add(menu_item)

            await session.commit()
            logger.info(f"✅ Successfully seeded {len(menu_items)} menu items")
            return True

<<<<<<< HEAD
    except Exception as e:
        logger.error(f"❌ Error seeding menu items: {e}")
        return False

async def main():
    """Main seeding function"""
    logger.info("🚀 Starting bulletproof database seeder...")
    
    # Setup database (this installs packages if missing)
    setup_result = setup_database()
    if not setup_result:
        logger.error("💥 Database setup failed")
        return False
    
    engine, AsyncSessionLocal, Base, MenuItem, menu_items = setup_result
    
    try:
        # Create tables
        if not await create_tables(engine, Base):
            return False
        
        # Seed data
        if not await seed_menu_items(AsyncSessionLocal, MenuItem, menu_items):
=======
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
>>>>>>> 765fdbc334cbad664aa5db1b05a3a1177f21a0c3
            return False
        
        logger.info("🎉 Seeding completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"💥 Seeding failed: {e}")
        return False
<<<<<<< HEAD
    finally:
        # Clean up engine
        if engine:
            await engine.dispose()

if __name__ == "_main_":
    # Run the seeding process
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
=======

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    
    # Exit with appropriate code
    exit(0 if success else 1)
>>>>>>> 765fdbc334cbad664aa5db1b05a3a1177f21a0c3
