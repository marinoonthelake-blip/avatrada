import unittest
import numpy as np
from src.services.quant.confidence_calculator import ConfidenceCalculator

class TestConfidenceCalculator(unittest.TestCase):

    def test_cold_start(self):
        print("\nTesting Cold Start (insufficient data)...")
        calc = ConfidenceCalculator(lookback_period=10)
        score = calc.calculate(100)
        self.assertEqual(score, 0.0)
        print("SUCCESS: Returns 0.0 when history is not populated.")

    def test_at_mean(self):
        print("\nTesting signal at the mean...")
        calc = ConfidenceCalculator(lookback_period=10)
        calc.hydrate([10.0] * 10) 
        score = calc.calculate(10.0)
        self.assertEqual(score, 0.0)
        print("SUCCESS: Returns 0.0 for signal at the mean.")

    def test_one_sigma_event(self):
        print("\nTesting signal at +1 standard deviation...")
        calc = ConfidenceCalculator(lookback_period=10)
        # Create a stable distribution
        history = [95.0, 105.0, 95.0, 105.0, 95.0, 105.0, 95.0, 105.0, 95.0, 105.0]
        calc.hydrate(history)
        mu, sigma = np.mean(history), np.std(history)
        one_sigma_signal = mu + sigma
        score = calc.calculate(one_sigma_signal)
        self.assertAlmostEqual(score, 1.0 / 3.0, places=5)
        print(f"SUCCESS: +1 sigma event returned confidence of ~{score:.2f} (expected 0.33).")

    def test_three_sigma_event(self):
        print("\nTesting signal at +3 standard deviations...")
        calc = ConfidenceCalculator(lookback_period=10)
        history = [95.0, 105.0, 95.0, 105.0, 95.0, 105.0, 95.0, 105.0, 95.0, 105.0]
        calc.hydrate(history)
        mu, sigma = np.mean(history), np.std(history)
        three_sigma_signal = mu + (3 * sigma)
        score = calc.calculate(three_sigma_signal)
        self.assertAlmostEqual(score, 1.0, places=5)
        print("SUCCESS: +3 sigma event returned confidence of 1.0.")

    def test_negative_z_score(self):
        print("\nTesting signal below the mean (negative Z-score)...")
        calc = ConfidenceCalculator(lookback_period=10)
        calc.hydrate([100.0] * 10)
        # Manually set a standard deviation to avoid 0
        calc.history.append(110.0)
        calc.history.append(90.0)
        score = calc.calculate(50.0)
        self.assertEqual(score, 0.0)
        print("SUCCESS: Negative Z-score event was correctly clipped to 0.0.")

if __name__ == '__main__':
    unittest.main()
