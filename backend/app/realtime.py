from typing import Dict, Set
from litestar import WebSocket, websocket
from litestar.status_codes import WS_1008_POLICY_VIOLATION
import asyncio
import json

# Use thread-safe data structures
class ConnectionManager:
    def _init_(self):
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

        for connection in connections:
            try:
                await connection.send_json({"type": event, "data": data})
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
        while True:
            # Receive and potentially process messages
            data = await websocket.receive_data()
            
            # Convert bytes to string if needed
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            try:
                # Parse and handle incoming messages
                message = json.loads(data)
                if message.get("type") == "new_comment":
                    # Broadcast to all clients in the comments room
                    await comment_manager.broadcast(
                        "comments", 
                        "new_comment", 
                        message.get("data", {})
                    )
            except json.JSONDecodeError:
                # Handle non-JSON messages (keep-alive pings)
                pass
    except Exception as e:
        print(f"Unexpected error in comments WebSocket: {e}")
        await comment_manager.disconnect("comments", websocket)

@websocket("/ws/orders")
async def orders_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for orders."""
    await order_manager.connect("orders", websocket)
    try:
        while True:
            data = await websocket.receive_data()
            
            # Convert bytes to string if needed
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            try:
                message = json.loads(data)
                if message.get("type") == "new_order":
                    await order_manager.broadcast(
                        "orders", 
                        "new_order", 
                        message.get("data", {})
                    )
                elif message.get("type") == "status_update":
                    await order_manager.broadcast(
                        "orders", 
                        "status_update", 
                        message.get("data", {})
                    )
            except json.JSONDecodeError:
                # Keep connection alive
                pass
    except Exception as e:
        print(f"Unexpected error in orders WebSocket: {e}")
        await order_manager.disconnect("orders", websocket)

# Optional: Generic room-based endpoint
@websocket("/ws/room/{room_name:str}")
async def room_websocket(websocket: WebSocket, room_name: str) -> None:
    """Generic WebSocket endpoint for any room."""
    # Add authentication/validation here
    if not room_name.isalnum() or len(room_name) > 50:
        await websocket.close(code=WS_1008_POLICY_VIOLATION)
        return

    manager = ConnectionManager()
    await manager.connect(room_name, websocket)
    try:
        while True:
            data = await websocket.receive_data()
            
            # Convert bytes to string if needed
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            # Echo message to all in room (or process as needed)
            try:
                message = json.loads(data)
                await manager.broadcast(room_name, "message", message)
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"Unexpected error in room WebSocket: {e}")
        await manager.disconnect(room_name, websocket)
