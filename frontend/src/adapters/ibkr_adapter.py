import asyncio
import nest_asyncio
from ib_async import IB
from src.core.config import settings
import logging

# Apply nest_asyncio to allow ib_async to run inside FastAPI's loop
nest_asyncio.apply()

class IBKRAdapter:
    def __init__(self):
        self.ib = IB()
        self.logger = logging.getLogger("IBKRAdapter")

    async def connect(self):
        if not self.ib.isConnected():
            try:
                self.logger.info(f"Connecting to IBKR at {settings.IBKR_HOST}:{settings.IBKR_PORT}...")
                await self.ib.connectAsync(
                    host=settings.IBKR_HOST,
                    port=settings.IBKR_PORT,
                    clientId=1,
                    timeout=10
                )
                self.logger.info("Successfully connected to IBKR Gateway.")
            except Exception as e:
                self.logger.error(f"Failed to connect to IBKR: {e}")
                raise

    async def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()
            self.logger.info("Disconnected from IBKR Gateway.")

    async def get_account_summary(self):
        if not self.ib.isConnected():
            await self.connect()
        return await self.ib.accountSummaryAsync()

# Singleton instance
ibkr_adapter = IBKRAdapter()
