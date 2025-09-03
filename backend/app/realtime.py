from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set

router = APIRouter()
rooms: Dict[str, Set[WebSocket]] = {}

async def join_room(room: str, ws: WebSocket):
    await ws.accept()
    s = rooms.setdefault(room, set())
    s.add(ws)

def leave_room(room: str, ws: WebSocket):
    if room in rooms and ws in rooms[room]:
        rooms[room].remove(ws)

async def broadcast(room: str, data: dict):
    dead = []
    for ws in rooms.get(room, set()):
        try:
            await ws.send_json(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        leave_room(room, ws)

@router.websocket("/ws/orders/{room}")
async def ws_orders(ws: WebSocket, room: str):
    await join_room(room, ws)
    try:
        while True:
            # keep-alive / client messages (not required)
            await ws.receive_text()
    except WebSocketDisconnect:
        leave_room(room, ws)

from fastapi import WebSocket, WebSocketDisconnect

class Hub:
    def __init__(self):
        self.clients = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, event: str, data: dict):
        dead = []
        for ws in self.clients:
            try:
                await ws.send_json({"type": event, "data": data})
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

hub = Hub()