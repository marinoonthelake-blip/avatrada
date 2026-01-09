import google.generativeai as genai
from src.core.config import settings
import logging

class AIRouter:
    def __init__(self):
        self.logger = logging.getLogger("AIRouter")
        try:
            # Initialize with the primary key
            genai.configure(api_key=settings.GOOGLE_API_KEY_1)

            # Strategic: High reasoning capability
            self.pro_model = genai.GenerativeModel('gemini-2.0-flash') 

            # Tactical: High speed, lower latency
            self.flash_model = genai.GenerativeModel('gemini-2.0-flash-lite')

            self.logger.info("AI Router Initialized with Gemini 2.0 Models")
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Router: {e}")

    async def get_strategic_analysis(self, prompt: str):
        """Strategic: Gemini 2.0 Flash for deep pre-market research."""
        try:
            response = await self.pro_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Strategic Analysis Failed: {e}")
            return None

    async def get_tactical_signal(self, prompt: str):
        """Tactical: Gemini 2.0 Flash-Lite for real-time signal validation."""
        try:
            response = await self.flash_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Tactical Signal Failed: {e}")
            return None

ai_router = AIRouter()
