import collections
import time
import logging
from enum import Enum

class VolatilityRegime(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"

class VelocityMonitor:
    """
    Monitors the rate of change of NLV over a rolling 60-minute window.
    Triggers a circuit breaker if the decline exceeds regime-aware thresholds.
    """
    def __init__(self, window_size: int = 60):
        self.history = collections.deque(maxlen=window_size)
        self.logger = logging.getLogger("VelocityMonitor")

        # Thresholds per Diamond Protocol
        self.thresholds = {
            VolatilityRegime.LOW: -0.0075,    # -0.75%
            VolatilityRegime.NORMAL: -0.0150, # -1.50%
            VolatilityRegime.HIGH: -0.0150    # -1.50%
        }
        self.is_tripped = False

    def add_snapshot(self, nlv: float, regime: VolatilityRegime = VolatilityRegime.NORMAL):
        """
        Adds a minute-by-minute NLV snapshot and checks for a velocity breach.
        Returns: True if a breach is detected, False otherwise.
        """
        self.history.append(nlv)

        # 1. Cold Start: Don't check until the window is full (60 minutes)
        if len(self.history) < self.history.maxlen:
            return False

        # 2. If already tripped, maintain the state
        if self.is_tripped:
            return True

        # 3. Calculate Velocity: (Current - 60m Ago) / 60m Ago
        nlv_current = self.history[-1]
        nlv_start = self.history[0]

        if nlv_start <= 0:
            return False

        velocity = (nlv_current - nlv_start) / nlv_start
        threshold = self.thresholds.get(regime, -0.0150)

        # 4. Check for Breach
        if velocity <= threshold:
            self.logger.critical(
                f"VELOCITY BREACH: NLV dropped {velocity:.2%} in 60 mins. "
                f"Threshold for {regime.name} is {threshold:.2%}. TRIP CIRCUIT BREAKER."
            )
            self.is_tripped = True
            return True

        return False

    def reset(self):
        """Resets the circuit breaker."""
        self.is_tripped = False
        self.history.clear()
        self.logger.info("Velocity Monitor Reset.")

velocity_monitor = VelocityMonitor()
