import asyncio
from src.services.ai.router import ai_router

async def test_ai_intelligence():
    print("--- Testing Intelligence Layer (Gemini 1.5 Flash) ---")

    test_prompt = "System Check: Respond with the single word 'DIAMOND' if you are online."

    try:
        print("Sending prompt to Gemini Flash...")
        response = await ai_router.get_tactical_signal(test_prompt)

        if response:
            print(f"AI Response: {response.strip()}")
            if "DIAMOND" in response.upper():
                print("SUCCESS: Intelligence Layer is ONLINE.")
            else:
                print("WARNING: AI responded but output was unexpected.")
        else:
            print("FAILURE: No response from AI Router.")

    except Exception as e:
        print(f"FAILURE: AI Router error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_intelligence())
