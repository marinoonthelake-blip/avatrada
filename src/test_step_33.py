import unittest
import time
from src.services.risk.monitors.wash_sale_monitor import WashSaleMonitor

class TestWashSaleMonitor(unittest.TestCase):

    def test_lockout_logic(self):
        print("\nTesting 15-minute lockout...")
        monitor = WashSaleMonitor()
        symbol = "AAPL"

        # Record a loss
        monitor.record_loss(symbol)

        # Check immediately
        status = monitor.get_restriction_status(symbol)
        self.assertTrue(status["restricted"])
        self.assertGreater(status["remaining_seconds"], 890) # Close to 900s
        print(f"SUCCESS: {symbol} correctly restricted. Remaining: {status['remaining_seconds']}s")

    def test_rotation_mapping(self):
        print("\nTesting Capital Rotation mapping...")
        monitor = WashSaleMonitor()

        target = monitor.get_rotation_target("SPY")
        self.assertEqual(target, "VOO")
        print(f"SUCCESS: SPY rotation target is {target}.")

        target = monitor.get_rotation_target("QQQ")
        self.assertEqual(target, "QLD")
        print(f"SUCCESS: QQQ rotation target is {target}.")

    def test_lockout_expiry(self):
        print("\nTesting lockout expiry (simulated)...")
        monitor = WashSaleMonitor()
        symbol = "TSLA"

        # Manually set a loss timestamp 16 minutes ago
        from datetime import datetime, timedelta
        monitor.loss_registry[symbol] = datetime.utcnow() - timedelta(minutes=16)

        status = monitor.get_restriction_status(symbol)
        self.assertFalse(status["restricted"])
        print("SUCCESS: Lockout correctly expired after 15 minutes.")

if __name__ == '__main__':
    unittest.main()
