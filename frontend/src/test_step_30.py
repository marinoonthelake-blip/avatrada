import unittest
from src.services.risk.monitors.velocity_monitor import VelocityMonitor, VolatilityRegime

class TestVelocityMonitor(unittest.TestCase):

    def test_cold_start(self):
        print("\nTesting Cold Start (window not full)...")
        monitor = VelocityMonitor(window_size=60)
        for i in range(59):
            monitor.add_snapshot(100000 - (i * 100))
        self.assertFalse(monitor.is_tripped)
        print("SUCCESS: Monitor did not trip before window was full.")

    def test_low_vol_breach(self):
        print("\nTesting Low Volatility Breach (-0.75%)...")
        monitor = VelocityMonitor(window_size=60)
        # Fill window with stable 100k
        for _ in range(59):
            monitor.add_snapshot(100000.0)

        # Drop to 99,200 (-0.8%)
        monitor.add_snapshot(99200.0, regime=VolatilityRegime.LOW)
        self.assertTrue(monitor.is_tripped)
        print("SUCCESS: Correctly tripped at -0.8% in LOW_VOL regime.")

    def test_high_vol_pass(self):
        print("\nTesting High Volatility Pass (at -0.8%)...")
        monitor = VelocityMonitor(window_size=60)
        for _ in range(59):
            monitor.add_snapshot(100000.0)

        # Drop to 99,200 (-0.8%) - Should NOT trip in HIGH_VOL (threshold is -1.5%)
        monitor.add_snapshot(99200.0, regime=VolatilityRegime.HIGH)
        self.assertFalse(monitor.is_tripped)
        print("SUCCESS: Did not trip at -0.8% in HIGH_VOL regime.")

    def test_high_vol_breach(self):
        print("\nTesting High Volatility Breach (-1.5%)...")
        monitor = VelocityMonitor(window_size=60)
        for _ in range(59):
            monitor.add_snapshot(100000.0)

        # Drop to 98,000 (-2.0%)
        monitor.add_snapshot(98000.0, regime=VolatilityRegime.HIGH)
        self.assertTrue(monitor.is_tripped)
        print("SUCCESS: Correctly tripped at -2.0% in HIGH_VOL regime.")

if __name__ == '__main__':
    unittest.main()
