import asyncio
import logging
from src.core.brain import brain
from src.adapters.thetadata_adapter import theta_adapter
from src.adapters.ibkr_adapter import ibkr_adapter

logger = logging.getLogger("LiveLoop")

async def run_live_cycle(symbol: str):
    """
    A single iteration of the live trading loop:
    1. Fetch fresh data.
    2. Get current NAV from IBKR.
    3. Process through the Brain.
    """
    try:
        # 1. Get Market Context
        price_data = await theta_adapter.get_stock_price(symbol)
        if not price_data or "price" not in price_data:
            return

        # 2. Get Account Context
        # In production, we'd pull real-time NAV from ibkr_adapter
        nav = 100000.0 

        # 3. Generate Mock Signals (for testing the loop)
        # In production, this comes from the ResearchAgent or Quant Models
        mock_signals = {"gamma": 0.75, "sentiment": 0.65}

        # 4. Execute via Brain
        result = await brain.process_signal(
            strategy_id="LIVE_BETA_01",
            symbol=symbol,
            signals=mock_signals,
            market_price=price_data["price"],
            nav=nav
        )

        if result["status"] == "SUBMITTED":
            logger.info(f"LIVE ORDER PLACED: {symbol}")

    except Exception as e:
        logger.error(f"Error in live cycle: {e}")

async def start_live_engine(watchlist: list):
    logger.info(f"Starting Avatrada Live Engine for: {watchlist}")
    await ibkr_adapter.connect()

    while True:
        for symbol in watchlist:
            await run_live_cycle(symbol)
            await asyncio.sleep(1) # Rate limit the loop
        await asyncio.sleep(5) # Cooldown between scans
