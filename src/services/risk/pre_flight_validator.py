from src.adapters.ibkr_adapter import ibkr_adapter
import logging

class PreFlightValidator:
    def __init__(self):
        self.logger = logging.getLogger("PreFlightValidator")
        self.MAX_POSITION_PCT = 0.20  # 20% NAV Cap
        self.FAT_FINGER_PCT = 0.05    # 5% Price Deviation

    async def validate(self, order: dict, market_price: float, nav: float) -> dict:
        """
        Runs pre-flight checks.
        Returns: {"valid": bool, "reason": str}
        """
        symbol = order.get("symbol")
        quantity = order.get("quantity")
        price = order.get("price", market_price) # Use limit price or market price

        notional_value = price * quantity

        # 1. Max Position Size Check
        if notional_value > (nav * self.MAX_POSITION_PCT):
            msg = f"REJECT: Order value ${notional_value:,.2f} exceeds 20% of NAV (${nav:,.2f})"
            self.logger.warning(msg)
            return {"valid": False, "reason": msg}

        # 2. Fat Finger Check (Price Deviation)
        if abs(price - market_price) / market_price > self.FAT_FINGER_PCT:
            msg = f"REJECT: Price ${price} deviates >5% from market ${market_price}"
            self.logger.warning(msg)
            return {"valid": False, "reason": msg}

        return {"valid": True, "reason": "PASSED"}

validator = PreFlightValidator()
