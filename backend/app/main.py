from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from .database import Base, engine
from .routers import menu, comments, orders, auth
from .config import settings
from .security import (
    rate_limit_middleware,
    trusted_host_middleware,
    security_headers_middleware,
)
from .middleware.logging import setup_logging
from .exceptions import global_exception_handler
from app.config import settings


# ✅ Setup logging before creating the app
setup_logging()

# ✅ Proper CORSConfig object (Litestar built-in)
cors_config = CORSConfig(
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# ✅ Create Litestar app
app = Litestar(
    route_handlers=[
        menu.router,
        comments.router,
        orders.router,
        auth.router,
    ],
    middleware=[
        rate_limit_middleware,
        trusted_host_middleware,
        security_headers_middleware,
    ],
    exception_handlers={Exception: global_exception_handler},
    cors_config=cors_config,
    debug=settings.debug,
)

# ✅ Startup event (create database tables)
@app.on_startup
async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ✅ Simple health check route
@get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
    }