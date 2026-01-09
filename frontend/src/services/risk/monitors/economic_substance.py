import json
import logging
from datetime import datetime
from sqlalchemy import text
from src.core.database import engine

class EconomicSubstanceLogger:
    """
    Enforces the logging of a pre-tax profit motive for every trade.
    Links trades to specific Alpha sources and market snapshots.
    """
    def __init__(self):
        self.logger = logging.getLogger("EconomicSubstance")

    async def log_rationale(self, trade_id: int, strategy_name: str, edge_source: str, snapshot: dict):
        """
        Records the economic rationale for a trade in the audit log.
        """
        # Per Doctrine: "Loss Harvesting" is prohibited as a rationale.
        if "tax" in edge_source.lower() or "harvest" in edge_source.lower():
            self.logger.error(f"PROHIBITED RATIONALE: '{edge_source}' for trade {trade_id}")
            return False

        payload = {
            "strategy": strategy_name,
            "edge_source": edge_source,
            "market_snapshot": snapshot
        }

        query = text("""
            INSERT INTO audit_log (event_type, entity_id, payload)
            VALUES (:event_type, :entity_id, :payload)
        """)

        try:
            async with engine.begin() as conn:
                await conn.execute(query, {
                    "event_type": "TRADE_RATIONALE",
                    "entity_id": str(trade_id),
                    "payload": json.dumps(payload)
                })
            self.logger.info(f"Rationale logged for trade {trade_id}: {edge_source}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to log economic substance: {e}")
            return False

substance_logger = EconomicSubstanceLogger()
