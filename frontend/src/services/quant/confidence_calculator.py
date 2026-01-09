import numpy as np
from collections import deque
from typing import Deque, List

class ConfidenceCalculator:
    """
    Calculates a real-time confidence score based on a rolling Z-score of a signal.
    Formula: confidence = (z_score_of_signal / 3.0).clip(0, 1)
    """
    def __init__(self, lookback_period: int = 60):
        if lookback_period <= 1:
            raise ValueError("Lookback period must be greater than 1.")
        self.lookback_period = lookback_period
        self.history: Deque[float] = deque(maxlen=lookback_period)

    def hydrate(self, historical_data: List[float]):
        """Fills the history with initial data."""
        if len(historical_data) > self.lookback_period:
            self.history.extend(historical_data[-self.lookback_period:])
        else:
            self.history.extend(historical_data)

    def calculate(self, current_signal_value: float) -> float:
        """
        Calculates confidence score based on existing history, then updates history.
        Returns a confidence score between 0.0 and 1.0.
        """
        # 1. Check if we have enough historical data to calculate a valid Z-score
        # We require a full window (or at least 90% of it) for statistical stability.
        if len(self.history) < self.lookback_period * 0.9:
            self.history.append(current_signal_value)
            return 0.0

        # 2. Calculate statistics based on the EXISTING history (the lookback window)
        data_array = np.array(self.history)
        mu = np.mean(data_array)
        sigma = np.std(data_array)

        # 3. Calculate Z-score for the NEW value against the OLD distribution
        if sigma < 1e-9:
            z_score = 0.0
        else:
            z_score = (current_signal_value - mu) / sigma

        # 4. Scale and clip per the Diamond Protocol
        confidence = np.clip(z_score / 3.0, 0, 1)

        # 5. Update history with the new value for the NEXT calculation
        self.history.append(current_signal_value)

        return float(confidence)
