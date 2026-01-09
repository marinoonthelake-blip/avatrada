import logging
from enum import Enum
from typing import Dict

class StrategyState(Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    PENDING_RESET = "PENDING_RESET"

class StreakBreaker:
    """
    Monitors consecutive losses per strategy.
    Triggers a PAUSE if the loss streak exceeds the threshold.
    """
    def __init__(self, threshold: int = 5):
        self.threshold = threshold
        self.strategy_states: Dict[str, StrategyState] = {}
        self.loss_counters: Dict[str, int] = {}
        self.logger = logging.getLogger("StreakBreaker")

    def record_result(self, strategy_id: str, pnl: float):
        """
        Records the result of a closed trade.
        A win or break-even (pnl >= 0) resets the counter.
        """
        if strategy_id not in self.loss_counters:
            self.loss_counters[strategy_id] = 0
            self.strategy_states[strategy_id] = StrategyState.RUNNING

        if pnl < 0:
            self.loss_counters[strategy_id] += 1
            self.logger.warning(f"Loss for {strategy_id}. Streak: {self.loss_counters[strategy_id]}")
        else:
            self.loss_counters[strategy_id] = 0
            self.logger.info(f"Win/Break-even for {strategy_id}. Streak reset.")

        # Check for breaker trigger
        if self.loss_counters[strategy_id] >= self.threshold:
            self.strategy_states[strategy_id] = StrategyState.PAUSED
            self.logger.critical(f"STREAK BREAKER: {strategy_id} hit {self.threshold} consecutive losses. PAUSING.")

    def get_state(self, strategy_id: str) -> StrategyState:
        return self.strategy_states.get(strategy_id, StrategyState.RUNNING)

    def reset_strategy(self, strategy_id: str):
        """Manually resets a strategy to RUNNING state."""
        self.loss_counters[strategy_id] = 0
        self.strategy_states[strategy_id] = StrategyState.RUNNING
        self.logger.info(f"Strategy {strategy_id} manually reset to RUNNING.")

streak_breaker = StreakBreaker()
