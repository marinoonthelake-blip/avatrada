import unittest
from src.services.risk.monitors.drawdown_scaler import DrawdownScaler

class TestDrawdownScaler(unittest.TestCase):

    def test_normal_operation(self):
        print("\nTesting Normal Operation (5% drawdown)...")
        scaler = DrawdownScaler(initial_nav=100000.0)
        # Drop to 95,000 (-5%)
        multiplier = scaler.get_multiplier(95000.0)
        self.assertEqual(multiplier, 1.0)
        print("SUCCESS: Multiplier is 1.0 at 5% drawdown.")

    def test_reduced_sizing(self):
        print("\nTesting Reduced Sizing (12% drawdown)...")
        scaler = DrawdownScaler(initial_nav=100000.0)
        # Drop to 88,000 (-12%)
        multiplier = scaler.get_multiplier(88000.0)
        self.assertEqual(multiplier, 0.5)
        print("SUCCESS: Multiplier is 0.5 at 12% drawdown.")

    def test_hard_stop(self):
        print("\nTesting Hard Stop (25% drawdown)...")
        scaler = DrawdownScaler(initial_nav=100000.0)
        # Drop to 75,000 (-25%)
        multiplier = scaler.get_multiplier(75000.0)
        self.assertEqual(multiplier, 0.0)
        self.assertTrue(scaler.hard_stop_triggered)
        print("SUCCESS: Multiplier is 0.0 at 25% drawdown. Hard stop latched.")

    def test_high_water_mark_update(self):
        print("\nTesting High Water Mark update...")
        scaler = DrawdownScaler(initial_nav=100000.0)
        # Increase to 120,000
        scaler.get_multiplier(120000.0)
        self.assertEqual(scaler.peak_nav, 120000.0)

        # Drop to 100,000 (This is now a -16.6% drawdown from 120k)
        multiplier = scaler.get_multiplier(100000.0)
        self.assertEqual(multiplier, 0.5)
        print("SUCCESS: Peak NAV updated and drawdown calculated correctly from new peak.")

if __name__ == '__main__':
    unittest.main()
