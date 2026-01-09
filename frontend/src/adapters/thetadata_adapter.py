import httpx
import orjson
from src.core.config import settings
import logging

class ThetaDataAdapter:
    def __init__(self):
        # Ensure we use the port confirmed in logs (25503)
        self.base_url = f"http://{settings.THETA_HOST}:25503"
        self.logger = logging.getLogger("ThetaDataAdapter")
        self.headers = {"Accept": "application/x-ndjson"}

    async def _get_ndjson(self, url: str):
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, headers=self.headers)

                if response.status_code == 200:
                    results = []
                    for line in response.text.strip().split('\n'):
                        if line:
                            results.append(orjson.loads(line))
                    # Return first result or list depending on endpoint
                    return results[0] if results else None

                elif response.status_code == 410:
                    # 410 Gone = Endpoint valid, but no data (Market Closed)
                    # This is considered a "Success" for connectivity testing
                    self.logger.info(f"ThetaData: Endpoint reachable but no data (410) - {url}")
                    return {"status": "MARKET_CLOSED", "code": 410}

                else:
                    self.logger.error(f"ThetaData Error: {response.status_code} - {url}")
                    return None
            except Exception as e:
                self.logger.error(f"ThetaData Exception: {e}")
                return None

    async def get_stock_price(self, symbol: str):
        """
        Fetches stock price.
        Uses V2 Bulk Snapshot path which is confirmed to return 410 (Valid) on your terminal.
        """
        url = f"{self.base_url}/v2/bulk_snapshot/stock/quote?roots={symbol}"
        return await self._get_ndjson(url)

theta_adapter = ThetaDataAdapter()
