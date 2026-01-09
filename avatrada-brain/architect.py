import os
import glob
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY")
LIBRARY_DIR = "library/markdown"

# PRIORITY FALLBACK LIST
# The script will try these in order for every single message.
MODEL_PRIORITY = [
    "models/gemini-3-pro-preview",
    "models/gemini-pro-latest",
    "models/gemini-2.5-pro",
    "models/gemini-1.5-pro" # Safety net
]

def load_bible():
    print(f"--- Loading Avatrada Research Library from {LIBRARY_DIR} ---")
    files = sorted(glob.glob(os.path.join(LIBRARY_DIR, "*.md")))
    
    if not files:
        print("❌ CRITICAL: No research files found.")
        return ""
        
    full_context = ""
    for f in files:
        filename = os.path.basename(f)
        with open(f, "r") as file:
            content = file.read()
            full_context += f"\n\n=== MODULE: {filename} ===\n{content}"
            
    print(f"✅ Loaded {len(files)} Engineering Modules.")
    print(f"🧠 Total Context Size: {len(full_context):,} characters")
    return full_context

def main():
    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY is missing.")
        return

    client = genai.Client(api_key=API_KEY)
    knowledge_base = load_bible()
    if not knowledge_base:
        return

    system_instruction = f"""
    You are the **Chief Architect of Avatrada**.
    
    YOUR KNOWLEDGE BASE:
    You have access to 66 verified Deep Research reports.
    Define formulas, architecture, and risk limits based STRICTLY on this data.
    
    === AVATRADA LIBRARY ===
    {knowledge_base}
    ========================
    """

    print("\n🚀 Avatrada Architect is Online.")
    print(f"💎 Model Priority: {MODEL_PRIORITY}")

    # Maintain chat history manually to allow model switching
    chat_history = [] 

    while True:
        try:
            user_input = input("\nAvatrada> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print("Thinking...")
            
            # --- FALLBACK LOGIC ---
            response_text = None
            
            for model_id in MODEL_PRIORITY:
                try:
                    # Attempt generation with current model
                    # We create a fresh chat session for this turn to inject history + new model
                    chat = client.chats.create(
                        model=model_id,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.3,
                        ),
                        history=chat_history
                    )
                    
                    response = chat.send_message(user_input)
                    response_text = response.text
                    
                    # If successful, save to history and break the fallback loop
                    chat_history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
                    chat_history.append(types.Content(role="model", parts=[types.Part(text=response_text)]))
                    
                    print(f"\n[{model_id}]:\n{response_text}\n")
                    break # Success! Stop trying other models.

                except ClientError as e:
                    # Catch 404 (Model not found) or 429 (Rate Limit)
                    err_msg = str(e)
                    if "404" in err_msg or "429" in err_msg or "503" in err_msg:
                        print(f"⚠️  {model_id} unavailable ({e.code}). Falling back...")
                        continue # Try next model
                    else:
                        raise e # Re-raise other errors (like Auth failures)
            
            if not response_text:
                print("❌ All models failed. Please check API Key or Quota.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
