from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Dictionary of rooms -> set of WebSocket connections
rooms: Dict[str, Set[WebSocket]] = {}


async def join_room(room: str, ws: WebSocket):
    """Add a WebSocket connection to a room."""
    await ws.accept()
    rooms.setdefault(room, set()).add(ws)


def leave_room(room: str, ws: WebSocket):
    """Remove a WebSocket connection from a room."""
    if room in rooms and ws in rooms[room]:
        rooms[room].remove(ws)
        if not rooms[room]:
            del rooms[room]  # cleanup empty rooms


async def broadcast(room: str, event: str, data: dict):
    """Send a message to all clients in a room."""
    dead = []
    for ws in rooms.get(room, set()):
        try:
            await ws.send_json({"type": event, "data": data})
        except Exception:
            dead.append(ws)
    for ws in dead:
        leave_room(room, ws)


@router.websocket("/ws/{room}")
async def ws_endpoint(ws: WebSocket, room: str):
    """
    General WebSocket endpoint.
    Example: /ws/orders or /ws/comments
    """
    await join_room(room, ws)
    try:
        while True:
            # Keep-alive: clients may send pings/messages
            await ws.receive_text()
    except WebSocketDisconnect:
        leave_room(room, ws)