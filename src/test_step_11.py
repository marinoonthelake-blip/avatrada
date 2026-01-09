import asyncio
from src.services.execution.order_gateway import order_gateway
from src.services.execution.firewall import firewall

async def test_firewall():
    print("--- Testing AI Execution Firewall ---")

    ai_order = {
        "symbol": "SPY",
        "action": "BUY",
        "quantity": 10,
        "source": "AI_GEMINI"
    }

    # Test 1: Unsigned AI Order (Should Fail)
    print("\n[1/2] Submitting Unsigned AI Order...")
    result = await order_gateway.submit_order(ai_order)
    if result["status"] == "REJECTED":
        print("SUCCESS: Firewall blocked unsigned AI order.")
    else:
        print(f"FAILURE: Firewall allowed unsigned order: {result}")

    # Test 2: Signed AI Order (Should Pass)
    print("\n[2/2] Submitting Signed AI Order...")
    # Simulate human signing
    signature = firewall.sign_order(ai_order)
    result = await order_gateway.submit_order(ai_order, signature)

    if result["status"] == "SUBMITTED":
        print("SUCCESS: Firewall accepted validly signed order.")
    else:
        print(f"FAILURE: Firewall rejected valid signature: {result}")

if __name__ == "__main__":
    asyncio.run(test_firewall())
