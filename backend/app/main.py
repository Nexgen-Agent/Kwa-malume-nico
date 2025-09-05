from dotenv import load_dotenv
load_dotenv()  # This loads environment variables from .env file

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from .db import Base, engine
from .routers import menu, comments, orders
from .realtime import comment_manager, order_manager

app = FastAPI(title="Malume Nico API")

# Allow frontend access (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Register routers
app.include_router(menu.router)
app.include_router(comments.router)
app.include_router(orders.router)

# Create DB tables on startup (async version)
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Health check
@app.get("/health")
async def health():
    return {"ok": True}

# ----------------------
# WEBSOCKETS
# ----------------------

@app.websocket("/ws/comments")
async def comments_ws(websocket: WebSocket):
    await comment_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive or process messages
            data = await websocket.receive_text()
            # You might want to process the message here
            # For example: await comment_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        comment_manager.disconnect(websocket)
    except Exception as e:
        # Handle other exceptions
        print(f"WebSocket error: {e}")
        comment_manager.disconnect(websocket)

@app.websocket("/ws/orders")
async def orders_ws(websocket: WebSocket):
    await order_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process order messages if needed
    except WebSocketDisconnect:
        order_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        order_manager.disconnect(websocket)

from fastapi.middleware.gzip import GZipMiddleware
# Add to your main app
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add these imports
from .routers import auth
from .auth import get_current_user

# Add auth router
app.include_router(auth.router)

# Add this to enable CORS for WebSocket authentication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],  # Your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)