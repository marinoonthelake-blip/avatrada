from src.services.execution.firewall import firewall
import logging

class OrderGateway:
    def __init__(self):
        self.logger = logging.getLogger("OrderGateway")

    async def submit_order(self, order: dict, signature: bytes = None):
        """
        The single entry point for all orders.
        Enforces the AI Firewall.
        """
        source = order.get("source", "UNKNOWN")

        if source == "AI_GEMINI":
            if not signature:
                self.logger.critical("BLOCKED: AI Order missing signature.")
                return {"status": "REJECTED", "reason": "MISSING_SIGNATURE"}

            if not firewall.verify_order(order, signature):
                self.logger.critical("BLOCKED: AI Order signature invalid.")
                return {"status": "REJECTED", "reason": "INVALID_SIGNATURE"}

            self.logger.info("APPROVED: AI Order signed by Human Operator.")

        # ... Proceed to IBKR Adapter ...
        return {"status": "SUBMITTED", "order": order}

order_gateway = OrderGateway()
