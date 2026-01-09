import logging
import asyncio
from src.services.quant.signal_aggregator import aggregator, Regime, SignalDecision
from src.services.risk.pre_flight_validator import validator
from src.services.risk.monitors.drawdown_scaler import drawdown_scaler
from src.services.risk.monitors.streak_breaker import streak_breaker, StrategyState
from src.services.risk.monitors.exclusion_list import exclusion_list
from src.services.risk.monitors.economic_substance import substance_logger
from src.services.execution.order_gateway import order_gateway

class AvatradaBrain:
    def __init__(self):
        self.logger = logging.getLogger("AvatradaBrain")

    async def process_signal(self, strategy_id: str, symbol: str, signals: dict, market_price: float, nav: float):
        """
        The Master Execution Flow:
        1. Check Exclusion List
        2. Check Strategy State (Streak Breaker)
        3. Aggregate Signals
        4. Apply Drawdown Scaling
        5. Pre-Flight Risk Check
        6. Execute & Log
        """
        self.logger.info(f"Processing signal for {symbol} from {strategy_id}")

        # 1. Compliance: Exclusion List
        if exclusion_list.is_restricted(symbol):
            self.logger.warning(f"BLOCK: {symbol} is on the restricted list.")
            return {"status": "REJECTED", "reason": "RESTRICTED_SYMBOL"}

        # 2. Risk: Streak Breaker
        if streak_breaker.get_state(strategy_id) != StrategyState.RUNNING:
            self.logger.warning(f"BLOCK: Strategy {strategy_id} is currently PAUSED.")
            return {"status": "REJECTED", "reason": "STRATEGY_PAUSED"}

        # 3. Quant: Signal Aggregation
        # For this example, we assume NORMAL regime.
        decision = aggregator.resolve(Regime.NORMAL, **signals)
        if decision == SignalDecision.PASS:
            return {"status": "SKIPPED", "reason": "LOW_CONFIDENCE"}

        # 4. Risk: Drawdown Scaling
        multiplier = drawdown_scaler.get_multiplier(nav)
        if multiplier <= 0:
            return {"status": "REJECTED", "reason": "HARD_STOP_ACTIVE"}

        # 5. Risk: Pre-Flight Validation
        order = {
            "symbol": symbol,
            "action": decision.value,
            "quantity": int(10 * multiplier), # Simplified sizing
            "price": market_price,
            "source": "ALGO_QUANT"
        }

        risk_check = await validator.validate(order, market_price, nav)
        if not risk_check["valid"]:
            return {"status": "REJECTED", "reason": risk_check["reason"]}

        # 6. Execution & Economic Substance Logging
        # In a real flow, we'd get a trade_id from the gateway
        execution_result = await order_gateway.submit_order(order)

        if execution_result["status"] == "SUBMITTED":
            # Log the "Why" for the IRS
            await substance_logger.log_rationale(
                trade_id=999, # Mock ID
                strategy_name=strategy_id,
                edge_source=f"Aggregated Signal: {signals}",
                snapshot={"price": market_price, "nav": nav}
            )

        return execution_result

brain = AvatradaBrain()
