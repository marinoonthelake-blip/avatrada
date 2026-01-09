import os
import google.genai as genai
from dotenv import load_dotenv

# Load Environment
load_dotenv("/home/avacado/avatrada/avatrada-brain/.env")
API_KEY = os.environ.get("GOOGLE_API_KEY")

print(f"🔧 Testing API Key: {API_KEY[:5]}...{API_KEY[-4:]}")

client = genai.Client(api_key=API_KEY)

# The exact ID causing the issue
TARGET_MODEL = "gemini-2.5-pro"

print(f"📡 Pinging {TARGET_MODEL}...")

try:
    response = client.models.generate_content(
        model=TARGET_MODEL,
        contents="System check. Reply with 'Online'."
    )
    print(f"✅ SUCCESS! Response: {response.text}")

except Exception as e:
    print("\n❌ CONNECTION FAILED")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    
    # Check if adding 'models/' fixes it
    print("\n🔄 Retrying with prefix 'models/'...")
    try:
        response = client.models.generate_content(
            model=f"models/{TARGET_MODEL}",
            contents="System check. Reply with 'Online'."
        )
        print(f"✅ SUCCESS! Response: {response.text}")
        print("💡 FIX FOUND: You need to prepend 'models/' to the ID.")
    except Exception as e2:
        print(f"❌ Retry Failed: {e2}")

