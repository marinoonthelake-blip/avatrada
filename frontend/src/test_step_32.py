import unittest
from src.services.risk.monitors.streak_breaker import StreakBreaker, StrategyState

class TestStreakBreaker(unittest.TestCase):

    def test_streak_trigger(self):
        print("\nTesting Streak Breaker trigger (5 losses)...")
        breaker = StreakBreaker(threshold=5)
        sid = "GAMMA_SCALPER"

        # Record 4 losses
        for _ in range(4):
            breaker.record_result(sid, -100.0)
            self.assertEqual(breaker.get_state(sid), StrategyState.RUNNING)

        # 5th loss should trigger pause
        breaker.record_result(sid, -50.0)
        self.assertEqual(breaker.get_state(sid), StrategyState.PAUSED)
        print("SUCCESS: Strategy paused after 5 consecutive losses.")

    def test_win_resets_streak(self):
        print("\nTesting win resets streak...")
        breaker = StreakBreaker(threshold=5)
        sid = "VOL_TARGET"

        # 3 losses
        for _ in range(3):
            breaker.record_result(sid, -100.0)

        # 1 win
        breaker.record_result(sid, 200.0)
        self.assertEqual(breaker.loss_counters[sid], 0)

        # 2 more losses (total 5, but not consecutive)
        for _ in range(2):
            breaker.record_result(sid, -100.0)

        self.assertEqual(breaker.get_state(sid), StrategyState.RUNNING)
        print("SUCCESS: Win correctly reset the loss counter.")

    def test_breakeven_resets_streak(self):
        print("\nTesting break-even resets streak...")
        breaker = StreakBreaker(threshold=5)
        sid = "MEAN_REV"

        breaker.record_result(sid, -100.0)
        breaker.record_result(sid, 0.0) # Break-even
        self.assertEqual(breaker.loss_counters[sid], 0)
        print("SUCCESS: Break-even (PnL=0) reset the counter.")

if __name__ == '__main__':
    unittest.main()
