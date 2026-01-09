import asyncio
import httpx
import time

async def test_celery_pipeline():
    print("--- Testing Asynchronous Task Pipeline ---")

    # Use the service name 'app'
    base_url = "http://app:8000"

    async with httpx.AsyncClient() as client:
        # 1. Submit Task
        print("\n[1/3] Submitting Backtest Task...")
        try:
            resp = await client.post(f"{base_url}/backtest/start?strategy=GammaScalp&days=30")
            resp.raise_for_status()
            data = resp.json()
            task_id = data["task_id"]
            print(f"Task Submitted. ID: {task_id}")
        except Exception as e:
            print(f"FAILURE: Could not submit task: {e}")
            return

        # 2. Poll for Progress
        print("\n[2/3] Polling for Completion...")
        for i in range(15):
            try:
                resp = await client.get(f"{base_url}/backtest/status/{task_id}")
                status = resp.json()
                state = status["status"]
                print(f"Poll {i+1}: Status = {state}")

                if state == "SUCCESS":
                    print(f"Result: {status['result']}")
                    print("SUCCESS: Task completed successfully.")
                    return
                elif state == "FAILURE":
                    print(f"FAILURE: Task failed on worker.")
                    return
            except Exception as e:
                print(f"Poll failed: {e}")

            await asyncio.sleep(1)

        print("FAILURE: Task did not complete in time.")

if __name__ == "__main__":
    asyncio.run(test_celery_pipeline())
