import asyncio
from sqlalchemy import text
from src.core.database import engine
from src.core.config import settings

async def test_connection():
    print(f"--- Testing Config for {settings.PROJECT_NAME} ---")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                print("SUCCESS: Database connection verified via Async Engine.")
            else:
                print(f"FAILURE: Unexpected result from DB: {val}")
    except Exception as e:
        print(f"FAILURE: Could not connect to DB. Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
