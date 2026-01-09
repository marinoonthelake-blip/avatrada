import asyncio
import unittest
from sqlalchemy import text
from src.core.database import engine
from src.services.risk.monitors.economic_substance import substance_logger

class TestEconomicSubstance(unittest.TestCase):

    async def test_log_valid_rationale(self):
        print("\nTesting Valid Rationale Logging...")
        trade_id = 999
        edge = "Gamma Imbalance > $2M at 4500 Strike"
        snapshot = {"spot": 4505.2, "vix": 14.5}

        success = await substance_logger.log_rationale(trade_id, "GAMMA_SCALPER", edge, snapshot)
        self.assertTrue(success)

        # Verify in DB
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT payload FROM audit_log WHERE entity_id = '999'"))
            row = result.fetchone()
            self.assertIn("Gamma Imbalance", row[0]["edge_source"])
        print("SUCCESS: Valid rationale persisted to Audit Log.")

    async def test_prohibited_rationale(self):
        print("\nTesting Prohibited Rationale (Tax Harvesting)...")
        success = await substance_logger.log_rationale(1000, "STRAT", "Tax Loss Harvesting", {})
        self.assertFalse(success)
        print("SUCCESS: Prohibited 'Tax' rationale was blocked.")

    async def test_immutability(self):
        print("\nTesting Immutability of Rationale...")
        # Attempt to delete the record created in the first test
        try:
            async with engine.begin() as conn:
                await conn.execute(text("DELETE FROM audit_log WHERE entity_id = '999'"))
            self.fail("Immutability trigger failed: Record was deleted.")
        except Exception as e:
            if "DIAMOND_PROTOCOL_VIOLATION" in str(e):
                print("SUCCESS: Immutability trigger protected the rationale.")
            else:
                raise e

def run_async_tests():
    loop = asyncio.get_event_loop()
    test = TestEconomicSubstance()
    loop.run_until_complete(test.test_log_valid_rationale())
    loop.run_until_complete(test.test_prohibited_rationale())
    loop.run_until_complete(test.test_immutability())

if __name__ == '__main__':
    run_async_tests()
