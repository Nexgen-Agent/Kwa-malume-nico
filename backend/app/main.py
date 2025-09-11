from dotenv import load_dotenv
load_dotenv()  # This loads environment variables from .env file

from litestar import Litestar, WebSocket, websocket
from litestar.middleware.cors import CORSMiddleware
from litestar.middleware.compression import CompressionMiddleware
from litestar.static_files import StaticFilesConfig
import asyncio
from .db import Base, engine
from .routers import menu, comments, orders, auth
from .realtime import comment_manager, order_manager
from .auth import get_current_user

# Create Litestar app instead of FastAPI
app = Litestar(
    title="Malume Nico API",
    route_handlers=[
        menu.router,
        comments.router, 
        orders.router,
        auth.router
    ],
    middleware=[
        # CORS middleware
        CORSMiddleware(
            allow_origins=["*"],  # In production, specify exact origins
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
        # Compression middleware (replaces GZipMiddleware)
        CompressionMiddleware(minimum_size=1000)
    ],
    cors_config={
        "allow_origins": ["http://localhost:3000", "https://yourfrontend.com"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
)

# Create DB tables on startup
@app.on_startup
async def startup_event() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Health check
@app.get("/health")
async def health() -> dict:
    return {"ok": True}

# ----------------------
# WEBSOCKETS
# ----------------------

@websocket("/ws/comments")
async def comments_ws(websocket: WebSocket) -> None:
    await comment_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive or process messages
            data = await websocket.receive_data()
            # You might want to process the message here
            # For example: await comment_manager.handle_message(websocket, data)
    except Exception as e:
        # Handle disconnection and errors
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
        comment_manager.disconnect(websocket)

@websocket("/ws/orders")
async def orders_ws(websocket: WebSocket) -> None:
    await order_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_data()
            # Process order messages if needed
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
        order_manager.disconnect(websocket)

# Optional: Serve static files if needed
# app = Litestar(..., static_files_config=[StaticFilesConfig(path="/path/to/static", directories=["static"])])
