import asyncio
from src.adapters.ibkr_adapter import ibkr_adapter
from src.core.config import settings

async def test_ibkr_connection():
    print(f"--- Testing IBKR Connection for Account {settings.IBKR_ACCOUNT} ---")
    try:
        await ibkr_adapter.connect()
        if ibkr_adapter.ib.isConnected():
            print("SUCCESS: Connected to IBKR Gateway.")
            # Verify account access
            accounts = ibkr_adapter.ib.managedAccounts()
            print(f"Managed Accounts: {accounts}")
            if settings.IBKR_ACCOUNT in accounts:
                print(f"SUCCESS: Account {settings.IBKR_ACCOUNT} is accessible.")
            else:
                print(f"WARNING: Account {settings.IBKR_ACCOUNT} not found in managed accounts list.")
        else:
            print("FAILURE: Connection established but ib.isConnected() is False.")
    except Exception as e:
        print(f"FAILURE: Could not connect to IBKR. Error: {e}")
    finally:
        await ibkr_adapter.disconnect()

if __name__ == "__main__":
    asyncio.run(test_ibkr_connection())
