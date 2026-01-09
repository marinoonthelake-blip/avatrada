import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

class WashSaleMonitor:
    """
    Monitors losses to prevent wash sale triggers and suggests capital rotation.
    Note: Per Diamond Protocol, 15-minute cooling off is enforced for re-entry.
    """
    def __init__(self):
        self.loss_registry: Dict[str, datetime] = {}
        self.logger = logging.getLogger("WashSaleMonitor")

        # Pre-defined rotation map for core assets
        self.rotation_map = {
            "SPY": "VOO",
            "VOO": "IVV",
            "IVV": "SPY",
            "QQQ": "QLD", # Note: QLD is 2x, use with caution or use ONEQ
            "IWM": "VTWO"
        }

    def record_loss(self, symbol: str):
        """Records a loss event for a symbol."""
        self.loss_registry[symbol] = datetime.utcnow()
        self.logger.info(f"Loss recorded for {symbol}. 15-minute lockout active.")

    def get_restriction_status(self, symbol: str) -> dict:
        """
        Checks if a symbol is currently under a cooling-off period.
        Returns: {"restricted": bool, "remaining_seconds": int}
        """
        last_loss = self.loss_registry.get(symbol)
        if not last_loss:
            return {"restricted": False, "remaining_seconds": 0}

        elapsed = datetime.utcnow() - last_loss
        lockout_duration = timedelta(minutes=15)

        if elapsed < lockout_duration:
            remaining = (lockout_duration - elapsed).total_seconds()
            return {"restricted": True, "remaining_seconds": int(remaining)}

        return {"restricted": False, "remaining_seconds": 0}

    def get_rotation_target(self, symbol: str) -> Optional[str]:
        """Suggests a correlated but different asset for capital rotation."""
        return self.rotation_map.get(symbol)

wash_sale_monitor = WashSaleMonitor()
