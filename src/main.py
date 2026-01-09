import asyncio
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from src.core.config import settings
from src.api.trading_routes import router as trading_router
from src.api.market_routes import router as market_router
from src.api.backtest_routes import router as backtest_router
from src.api.websocket_gateway import router as ws_router, redis_connector
from src.services.execution.live_loop import start_live_engine

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def system_heartbeat():
    redis = Redis.from_url(f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0", decode_responses=True)
    while True:
        payload = {"type": "HEARTBEAT", "timestamp": datetime.utcnow().isoformat()}
        await redis.publish("system_events", json.dumps(payload))
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_connector())
    asyncio.create_task(system_heartbeat())
    # Launch the Live Engine in the background
    # asyncio.create_task(start_live_engine(["SPY", "QQQ", "TSLA"]))

@app.get("/health")
async def health():
    return {"status": "online", "engine": settings.PROJECT_NAME}

app.include_router(trading_router)
app.include_router(market_router)
app.include_router(backtest_router)
app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
