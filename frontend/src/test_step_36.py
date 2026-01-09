import asyncio
import unittest
from src.core.brain import brain

class TestSystemIntegration(unittest.TestCase):

    async def test_full_execution_flow(self):
        print("\nTesting Full Signal-to-Execution Flow...")

        # Inputs
        strategy_id = "GAMMA_SCALPER"
        symbol = "TSLA" # Not on restricted list
        signals = {"gamma": 0.8, "sentiment": 0.7} # Strong Buy
        market_price = 250.0
        nav = 100000.0

        result = await brain.process_signal(strategy_id, symbol, signals, market_price, nav)

        self.assertEqual(result["status"], "SUBMITTED")
        print(f"SUCCESS: Signal processed through all layers. Result: {result['status']}")

    async def test_restricted_block(self):
        print("\nTesting Restricted Symbol Block...")
        # AAPL is on the restricted list
        result = await brain.process_signal("STRAT", "AAPL", {"gamma": 0.9}, 150.0, 100000.0)
        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "RESTRICTED_SYMBOL")
        print("SUCCESS: Restricted symbol correctly blocked by Brain.")

    async def test_low_confidence_pass(self):
        print("\nTesting Low Confidence Pass...")
        # Weak signals that won't hit the 0.6 threshold
        signals = {"gamma": 0.3, "sentiment": 0.2}
        result = await brain.process_signal("STRAT", "TSLA", signals, 250.0, 100000.0)
        self.assertEqual(result["status"], "SKIPPED")
        print("SUCCESS: Low confidence signal correctly skipped.")

def run_async_tests():
    loop = asyncio.get_event_loop()
    test = TestSystemIntegration()
    loop.run_until_complete(test.test_full_execution_flow())
    loop.run_until_complete(test.test_restricted_block())
    loop.run_until_complete(test.test_low_confidence_pass())

if __name__ == '__main__':
    run_async_tests()
