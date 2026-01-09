from src.services.ai.router import ai_router
import logging

class ResearchAgent:
    def __init__(self):
        self.logger = logging.getLogger("ResearchAgent")

    async def analyze_market_condition(self, symbol: str, price_data: dict = None):
        """
        Orchestrates a research cycle.
        If price_data is None, it asks for a general sentiment check.
        """
        context = f"Market Data: {price_data}" if price_data else "Market Data: Unavailable (Market Closed)"

        prompt = f"""
        Role: Quantitative Trading Analyst.
        Task: Analyze the following context for {symbol}.
        Context: {context}

        Output: Provide a brief strategic outlook.
        Format: JSON with keys 'signal' (BUY/SELL/HOLD) and 'confidence' (0.0-1.0).
        """

        # Route to Tactical Model (Flash) for speed
        return await ai_router.get_tactical_signal(prompt)

research_agent = ResearchAgent()
