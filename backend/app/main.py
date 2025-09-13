from litestar import Litestar
from litestar.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import menu, comments, orders, auth
from .config import settings
from .security import rate_limit_middleware, trusted_host_middleware, security_headers_middleware
from .middleware.logging import LoggingMiddleware
from .exceptions import global_exception_handler

app = Litestar(
    title="Malume Nico API",
    version="1.0.0",
    route_handlers=[
        menu.router,
        comments.router, 
        orders.router,
        auth.router
    ],
    middleware=[
        LoggingMiddleware,
        rate_limit_middleware,
        trusted_host_middleware,
        security_headers_middleware,
        CORSMiddleware(
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
    ],
    exception_handlers={
        Exception: global_exception_handler
    },
    cors_config={
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
    debug=settings.debug
)

@app.on_startup
async def startup_event() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment
    }