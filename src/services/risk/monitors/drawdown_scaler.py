import logging
from decimal import Decimal

class DrawdownScaler:
    """
    Adjusts position sizing based on the portfolio's drawdown from its peak NAV.
    - 10% Drawdown -> 0.5x Sizing
    - 20% Drawdown -> 0.0x Sizing (Hard Stop)
    """
    def __init__(self, initial_nav: float):
        self.peak_nav = float(initial_nav)
        self.logger = logging.getLogger("DrawdownScaler")
        self.hard_stop_triggered = False

    def get_multiplier(self, current_nav: float) -> float:
        """
        Calculates the sizing multiplier based on current drawdown.
        """
        if self.hard_stop_triggered:
            return 0.0

        current_nav = float(current_nav)

        # Update Peak NAV (High Water Mark)
        if current_nav > self.peak_nav:
            self.peak_nav = current_nav
            self.logger.info(f"New High Water Mark: ${self.peak_nav:,.2f}")

        drawdown = (current_nav - self.peak_nav) / self.peak_nav

        # 1. Hard Stop Check (20% Drawdown)
        if drawdown <= -0.20:
            self.logger.critical(f"CRITICAL DRAWDOWN: {drawdown:.2%}. Triggering Hard Stop.")
            self.hard_stop_triggered = True
            return 0.0

        # 2. Reduced Sizing Check (10% Drawdown)
        if drawdown <= -0.10:
            self.logger.warning(f"DRAWDOWN ALERT: {drawdown:.2%}. Scaling exposure to 0.5x.")
            return 0.5

        # 3. Normal Sizing
        return 1.0

    def reset(self, new_nav: float):
        """Resets the scaler with a new capital base."""
        self.peak_nav = float(new_nav)
        self.hard_stop_triggered = False
        self.logger.info(f"Drawdown Scaler Reset. New Peak: ${self.peak_nav:,.2f}")

# Initialize with a placeholder; in production, this loads from the DB
drawdown_scaler = DrawdownScaler(initial_nav=50000.0)
