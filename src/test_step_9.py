import asyncio
import httpx
from src.adapters.thetadata_adapter import theta_adapter

async def test_theta_connection():
    print("--- Testing ThetaData V3 Connectivity (Port 25503) ---")

    server_url = "http://theta-terminal:25503"

    # 1. Wait for the server to become responsive
    print(f"Waiting for {server_url} to wake up...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        for i in range(60):
            try:
                # We expect a response, even if it's 404. That means it's alive.
                await client.get(server_url)
                print(f"SUCCESS: Theta Terminal is ONLINE (Network Path Open).")
                break
            except Exception:
                pass
            if i % 5 == 0: print(f"Still waiting... ({i}s)")
            await asyncio.sleep(1)
        else:
            print("FAILURE: Theta Terminal did not respond on port 25503.")
            return

    # 2. Attempt to fetch SPY quote
    print("Fetching SPY quote...")
    quote = await theta_adapter.get_stock_price("SPY")

    if quote:
        print(f"SUCCESS: Received data for SPY: {quote}")
    else:
        # If market is closed, V3 often returns empty or specific headers
        print("SUCCESS: Server reachable. (Note: Data may be empty if Market Closed)")

if __name__ == "__main__":
    asyncio.run(test_theta_connection())
