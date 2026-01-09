import unittest
from src.services.quant.signal_aggregator import SignalAggregationEngine, Regime, SignalDecision

class TestSignalAggregator(unittest.TestCase):

    def setUp(self):
        """Set up a test instance of the aggregator."""
        self.weights = {"gamma": 0.6, "sentiment": 0.4}
        self.threshold = 0.5
        self.aggregator = SignalAggregationEngine(self.weights, self.threshold)

    def test_high_vol_unanimous_buy(self):
        print("\nTesting HIGH_VOL: Unanimous Buy...")
        decision = self.aggregator.resolve(Regime.HIGH_VOLATILITY, gamma=0.8, sentiment=0.6)
        self.assertEqual(decision, SignalDecision.BUY)
        print("SUCCESS: Correctly decided BUY.")

    def test_high_vol_no_consensus(self):
        print("\nTesting HIGH_VOL: No Consensus (Mixed Signals)...")
        decision = self.aggregator.resolve(Regime.HIGH_VOLATILITY, gamma=0.8, sentiment=-0.7)
        self.assertEqual(decision, SignalDecision.PASS)
        print("SUCCESS: Correctly decided PASS.")

    def test_high_vol_one_weak_signal(self):
        print("\nTesting HIGH_VOL: No Consensus (Weak Signal)...")
        decision = self.aggregator.resolve(Regime.HIGH_VOLATILITY, gamma=0.8, sentiment=0.2) # 0.2 is below unanimous_threshold
        self.assertEqual(decision, SignalDecision.PASS)
        print("SUCCESS: Correctly decided PASS.")

    def test_normal_vol_weighted_buy(self):
        print("\nTesting NORMAL: Weighted Vote Buy...")
        # Score = (0.9 * 0.6) + (0.2 * 0.4) = 0.54 + 0.08 = 0.62
        # 0.62 > 0.5 threshold -> BUY
        decision = self.aggregator.resolve(Regime.NORMAL, gamma=0.9, sentiment=0.2)
        self.assertEqual(decision, SignalDecision.BUY)
        print("SUCCESS: Correctly decided BUY.")

    def test_normal_vol_weighted_sell(self):
        print("\nTesting NORMAL: Weighted Vote Sell...")
        # Score = (-0.8 * 0.6) + (-0.5 * 0.4) = -0.48 - 0.20 = -0.68
        # -0.68 < -0.5 threshold -> SELL
        decision = self.aggregator.resolve(Regime.NORMAL, gamma=-0.8, sentiment=-0.5)
        self.assertEqual(decision, SignalDecision.SELL)
        print("SUCCESS: Correctly decided SELL.")

    def test_normal_vol_weighted_pass(self):
        print("\nTesting NORMAL: Weighted Vote Pass (Below Threshold)...")
        # Score = (0.5 * 0.6) + (0.3 * 0.4) = 0.30 + 0.12 = 0.42
        # 0.42 is not > 0.5 threshold -> PASS
        decision = self.aggregator.resolve(Regime.NORMAL, gamma=0.5, sentiment=0.3)
        self.assertEqual(decision, SignalDecision.PASS)
        print("SUCCESS: Correctly decided PASS.")

if __name__ == '__main__':
    unittest.main()
