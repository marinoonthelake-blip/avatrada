import logging
from enum import Enum

class Regime(Enum):
    NORMAL = "NORMAL"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"

class SignalDecision(Enum):
    PASS = "PASS"
    BUY = "BUY"
    SELL = "SELL"

class SignalAggregationEngine:
    """
    Aggregates multiple signal confidences into a single decision based on market regime.
    """
    def __init__(self, weights: dict, vote_threshold: float, unanimous_threshold: float = 0.5):
        self.weights = weights
        self.vote_threshold = vote_threshold
        self.unanimous_threshold = unanimous_threshold
        self.logger = logging.getLogger("SignalAggregator")
        self.logger.info(f"Initialized with weights: {weights}, vote_threshold: {vote_threshold}")

    def resolve(self, regime: Regime, **signals: float) -> SignalDecision:
        """
        Resolves signals based on the provided regime.
        Args:
            regime: The current market regime (NORMAL or HIGH_VOLATILITY).
            **signals: Keyword arguments of signal confidences, e.g., gamma=0.7, sentiment=-0.4
        """
        if regime == Regime.HIGH_VOLATILITY:
            return self._handle_high_vol(signals)
        elif regime == Regime.NORMAL:
            return self._handle_normal_vol(signals)
        else:
            self.logger.error(f"Unknown regime: {regime}")
            return SignalDecision.PASS

    def _handle_high_vol(self, signals: dict[str, float]) -> SignalDecision:
        """UNANIMOUS: All signals must agree (all positive or all negative)."""
        self.logger.info(f"[HIGH_VOL] Resolving signals: {signals}")

        if not signals:
            return SignalDecision.PASS

        buy_signals = all(conf > self.unanimous_threshold for conf in signals.values())
        sell_signals = all(conf < -self.unanimous_threshold for conf in signals.values())

        if buy_signals:
            self.logger.info("[HIGH_VOL] Decision: UNANIMOUS BUY")
            return SignalDecision.BUY
        if sell_signals:
            self.logger.info("[HIGH_VOL] Decision: UNANIMOUS SELL")
            return SignalDecision.SELL

        self.logger.info("[HIGH_VOL] Decision: PASS (No consensus)")
        return SignalDecision.PASS

    def _handle_normal_vol(self, signals: dict[str, float]) -> SignalDecision:
        """WEIGHTED VOTE: Score = Sum(confidence * weight)."""
        self.logger.info(f"[NORMAL] Resolving signals: {signals}")

        score = 0.0
        for name, confidence in signals.items():
            weight = self.weights.get(name, 0.0)
            score += confidence * weight

        self.logger.info(f"[NORMAL] Weighted Score: {score:.4f} | Threshold: {self.vote_threshold}")

        if score > self.vote_threshold:
            self.logger.info(f"[NORMAL] Decision: BUY (Score > {self.vote_threshold})")
            return SignalDecision.BUY
        if score < -self.vote_threshold:
            self.logger.info(f"[NORMAL] Decision: SELL (Score < {-self.vote_threshold})")
            return SignalDecision.SELL

        self.logger.info("[NORMAL] Decision: PASS (Score within threshold)")
        return SignalDecision.PASS

# Default instantiation based on doctrine
default_weights = {
    "gamma": 0.5,
    "sentiment": 0.3,
    "technicals": 0.2
}
aggregator = SignalAggregationEngine(weights=default_weights, vote_threshold=0.6)
