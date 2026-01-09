import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from src.core.config import settings
import logging

router = APIRouter(tags=["WebSockets"])
logger = logging.getLogger("WebSocketGateway")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Client connected to WebSocket.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("Client disconnected.")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Handle case where client disconnects between check and send
                pass

manager = ConnectionManager()

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def redis_connector():
    """Background task to listen to Redis and broadcast to WebSockets."""
    redis = Redis.from_url(f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0", decode_responses=True)
    pubsub = redis.pubsub()
    # Subscribe to all relevant channels
    await pubsub.subscribe("system_events", "market_data", "trade_updates")

    logger.info("Redis PubSub listener started.")
    async for message in pubsub.listen():
        if message["type"] == "message":
            await manager.broadcast(message["data"])
