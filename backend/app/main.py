from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import menu, comments, orders
from .realtime import comment_manager, order_manager

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Malume Nico API")

# Allow frontend access (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Register routers
app.include_router(menu.router)
app.include_router(comments.router)
app.include_router(orders.router)

# Health check
@app.get("/health")
async def health():
    return {"ok": True}


# ----------------------
# WEBSOCKETS
# ----------------------

@app.websocket("/ws/comments")
async def comments_ws(ws: WebSocket):
    await comment_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        comment_manager.disconnect(ws)


@app.websocket("/ws/orders")
async def orders_ws(ws: WebSocket):
    await order_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        order_manager.disconnect(ws)