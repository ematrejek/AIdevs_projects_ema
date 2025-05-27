from openai import AsyncOpenAI
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def completion(self, messages: List[Dict[str, Any]], model: str = "gpt-4"):
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response
        except Exception as e:
            raise Exception(f"Error in OpenAI completion: {str(e)}") 