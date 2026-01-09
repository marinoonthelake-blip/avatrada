import asyncio
import websockets
import json
from redis.asyncio import Redis
from src.core.config import settings

async def test_websocket_gateway():
    print("--- Testing Real-Time WebSocket Gateway ---")

    uri = "ws://app:8000/ws/stream"

    # 1. Connect to WebSocket
    print("Connecting to WebSocket...")
    try:
        async with websockets.connect(uri) as websocket:
            print("SUCCESS: Connected to WebSocket.")

            # 2. Simulate Backend Event (Publish to Redis)
            print("Publishing test message to Redis 'market_data' channel...")
            redis = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            test_payload = json.dumps({"symbol": "SPY", "price": 450.50, "type": "TEST_TICK"})
            await redis.publish("market_data", test_payload)
            await redis.close()

            # 3. Wait for Broadcast
            print("Waiting for broadcast...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received: {message}")

                if "TEST_TICK" in message:
                    print("SUCCESS: Redis -> WebSocket broadcast verified.")
                else:
                    print("FAILURE: Received unexpected message.")
            except asyncio.TimeoutError:
                print("FAILURE: Timed out waiting for broadcast.")

    except Exception as e:
        print(f"FAILURE: Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_gateway())
