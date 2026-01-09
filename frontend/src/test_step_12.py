import asyncio
from src.services.risk.pre_flight_validator import validator

async def test_risk_checks():
    print("--- Testing Pre-Flight Risk Validator ---")

    # Mock Account State
    NAV = 100_000.00
    MARKET_PRICE = 450.00 # SPY

    # Test 1: Oversized Order (30% NAV)
    print("\n[1/2] Testing Max Position Size (30% NAV)...")
    oversized_order = {"symbol": "SPY", "quantity": 67, "price": 450.00} # ~$30k
    res1 = await validator.validate(oversized_order, MARKET_PRICE, NAV)

    if not res1["valid"] and "exceeds 20%" in res1["reason"]:
        print(f"SUCCESS: Blocked oversized order. Reason: {res1['reason']}")
    else:
        print(f"FAILURE: Failed to block oversized order: {res1}")

    # Test 2: Fat Finger (10% Deviation)
    print("\n[2/2] Testing Fat Finger Check (Limit $500 vs Market $450)...")
    fat_finger_order = {"symbol": "SPY", "quantity": 10, "price": 500.00}
    res2 = await validator.validate(fat_finger_order, MARKET_PRICE, NAV)

    if not res2["valid"] and "deviates >5%" in res2["reason"]:
        print(f"SUCCESS: Blocked fat finger order. Reason: {res2['reason']}")
    else:
        print(f"FAILURE: Failed to block fat finger order: {res2}")

if __name__ == "__main__":
    asyncio.run(test_risk_checks())
