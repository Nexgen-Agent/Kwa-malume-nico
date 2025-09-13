from typing import Dict, Set
from litestar import WebSocket, websocket
from litestar.status_codes import WS_1008_POLICY_VIOLATION
import asyncio
import json

# Use thread-safe data structures
class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()  # Lock for thread safety

    async def connect(self, room: str, websocket: WebSocket):
        """Add a WebSocket connection to a room."""
        await websocket.accept()
        async with self._lock:
            if room not in self.rooms:
                self.rooms[room] = set()
            self.rooms[room].add(websocket)

    async def disconnect(self, room: str, websocket: WebSocket):
        """Remove a WebSocket connection from a room."""
        async with self._lock:
            if room in self.rooms and websocket in self.rooms[room]:
                self.rooms[room].remove(websocket)
                if not self.rooms[room]:
                    del self.rooms[room]

    async def broadcast(self, room: str, event: str, data: dict):
        """Send a message to all clients in a room."""
        dead_connections = []
        async with self._lock:
            connections = self.rooms.get(room, set()).copy()

        message = {"type": event, "data": data}

        for connection in connections:
            try:
                await connection.send_json(message)
            except (RuntimeError, ConnectionError):
                dead_connections.append(connection)

        # Clean up dead connections
        if dead_connections:
            async with self._lock:
                for connection in dead_connections:
                    if room in self.rooms and connection in self.rooms[room]:
                        self.rooms[room].remove(connection)
                if room in self.rooms and not self.rooms[room]:
                    del self.rooms[room]

# Create manager instances for different purposes
comment_manager = ConnectionManager()
order_manager = ConnectionManager()

@websocket("/ws/comments")
async def comments_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for comments."""
    await comment_manager.connect("comments", websocket)
    try:
        # The loop below keeps the connection alive, waiting for it to close
        async for _ in websocket.iter_bytes():
            pass
    finally:
        await comment_manager.disconnect("comments", websocket)

@websocket("/ws/orders")
async def orders_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for orders."""
    await order_manager.connect("orders", websocket)
    try:
        # The loop below keeps the connection alive, waiting for it to close
        async for _ in websocket.iter_bytes():
            pass
    finally:
        await order_manager.disconnect("orders", websocket)

# Optional: Generic room-based endpoint
@websocket("/ws/room/{room_name:str}")
async def room_websocket(websocket: WebSocket, room_name: str) -> None:
    """Generic WebSocket endpoint for any room."""
    if not room_name.isalnum() or len(room_name) > 50:
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
        return

    # Use a shared manager or one from a dependency
    # This example re-uses the comment_manager for simplicity.
    await comment_manager.connect(room_name, websocket)
    try:
        # The loop below keeps the connection alive, waiting for it to close
        async for _ in websocket.iter_bytes():
            pass
    finally:
        await comment_manager.disconnect(room_name, websocket)