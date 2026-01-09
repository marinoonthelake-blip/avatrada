from google.genai import types
from google import genai
import base64, io, PIL.Image, streamlit as st

class ChatBehavior:
    def __init__(self, api_key, model_hierarchy):
        self.client = genai.Client(api_key=api_key)
        self.model_hierarchy = model_hierarchy

    def process_image_to_b64(self, file_source):
        try:
            if hasattr(file_source, 'getvalue'): data = file_source.getvalue()
            elif hasattr(file_source, 'read'): data = file_source.read()
            else: data = file_source
            img = PIL.Image.open(io.BytesIO(data))
            img.thumbnail((1024, 1024))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
        except Exception: return None

    def prepare_recall_payload(self, messages):
        payload = []
        for m in messages:
            parts = []
            content = m["content"] if isinstance(m["content"], list) else [m["content"]]
            for p in content:
                if isinstance(p, str) and p.startswith("data:image"):
                    b64 = p.split(",")[1]
                    parts.append(types.Part(inline_data=types.Blob(mime_type="image/png", data=base64.b64decode(b64))))
                else: parts.append(types.Part(text=str(p)))
            payload.append(types.Content(role="model" if m["role"]=="assistant" else "user", parts=parts))
        return payload

    def execute_with_fallback(self, tier, contents, instructions, doctrines, library, logger):
        is_locked = st.session_state.get("doctrine_lock", True)
        
        # --- SMART LOCK DIRECTIVE (v6.3.3) ---
        # Allows coding skills but restricts project facts.
        lock_directive = ""
        if is_locked:
            lock_directive = """
            CRITICAL PROTOCOL: DOCTRINE LOCK ACTIVE.
            1. FACTS: You must strictly adhere to the project structure, filenames, and definitions in the DOCTRINES and STATES below. Do not invent new architecture.
            2. SKILLS: You ARE PERMITTED to use your general training data for coding syntax, standard libraries (Python, React, Docker), and best practices.
            3. UNKNOWN: If a specific project definition is missing, explicitly ask for it. Do not guess.
            """
        
        system_prompt = f"""
        {lock_directive}
        
        === LEVEL 1: IMMUTABLE LAWS (Doctrines) ===
        {doctrines}
        
        === LEVEL 2: CURRENT REALITY (Library & States) ===
        {library}
        
        === LEVEL 3: OPERATING MANUAL (Identity) ===
        {instructions}
        """
        
        errors = []
        for model_id in self.model_hierarchy[tier]:
            try:
                # Disable Safety Settings to prevent false positives on code generation
                res = self.client.models.generate_content(
                    model=model_id,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt, 
                        temperature=0.0,
                        safety_settings=[
                            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE")
                        ]
                    ),
                    contents=contents
                )
                
                if not res.text:
                    err_msg = f"Empty response from {model_id}. Finish Reason: {res.candidates[0].finish_reason if res.candidates else 'Unknown'}"
                    errors.append(err_msg)
                    logger.error(err_msg)
                    continue

                return str(res.text)

            except Exception as e:
                err_str = f"{model_id} Error: {str(e)}"
                errors.append(err_str)
                logger.error(err_str)
                continue
        
        if errors:
            st.error(f"🚨 DEBUG TRACE: {'; '.join(errors)}")
        return None

def get_chat_behavior(api_key, hierarchy):
    return ChatBehavior(api_key, hierarchy)
