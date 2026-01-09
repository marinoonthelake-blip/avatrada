import asyncio
import httpx

async def test_api_layer():
    print("--- Testing API Transport Layer ---")

    # Use the service name 'app' instead of 'localhost'
    base_url = "http://app:8000"

    async with httpx.AsyncClient() as client:
        # 1. Health Check
        print("\n[1/3] Testing Health Endpoint...")
        try:
            resp = await client.get(f"{base_url}/health")
            print(f"Status: {resp.status_code}, Body: {resp.json()}")

            if resp.status_code != 200:
                print("FAILURE: Health check failed.")
                return
        except Exception as e:
            print(f"FAILURE: Could not connect to API: {e}")
            return

        # 2. Market Data (SPY)
        print("\n[2/3] Testing Market Data Endpoint (SPY)...")
        resp = await client.get(f"{base_url}/market/quote/SPY")
        print(f"Status: {resp.status_code}")
        # Note: 404 is acceptable if market is closed, but 500 is a failure.
        if resp.status_code == 500:
            print("FAILURE: Internal Server Error on Market Data.")
            return

        # 3. Order Submission (Validation Failure Test)
        print("\n[3/3] Testing Order Endpoint (Oversized Order)...")
        bad_order = {
            "symbol": "SPY",
            "action": "BUY",
            "quantity": 10000, # Huge quantity
            "price": 450.00,
            "source": "MANUAL_USER"
        }
        resp = await client.post(f"{base_url}/trading/order", json=bad_order)
        print(f"Status: {resp.status_code}, Body: {resp.json()}")

        if resp.status_code == 400:
            print("SUCCESS: API correctly rejected invalid order.")
        else:
            print("FAILURE: API did not reject invalid order.")

if __name__ == "__main__":
    asyncio.run(test_api_layer())
