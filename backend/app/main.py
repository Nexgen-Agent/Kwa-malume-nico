import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base
from .routers import menu, orders
from .realtime import router as ws_router

app = FastAPI(title="Malume Nico API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(ws_router)

@app.on_event("startup")
async def startup():
    # ensure DB & tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"ok": True}

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import menu, orders
from .realtime import hub

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Live Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: lock down in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(menu.router)
app.include_router(orders.router)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await hub.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        hub.disconnect(ws)