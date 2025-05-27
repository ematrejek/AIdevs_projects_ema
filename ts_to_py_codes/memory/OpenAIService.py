import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any

class OpenAIService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY nie jest ustawiony w zmiennych środowiskowych")
        self.client = AsyncOpenAI(api_key=api_key)

    async def extract_queries(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        Wyodrębnia kluczowe zapytania z konwersacji.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Wyodrębnij kluczowe zapytania z konwersacji."},
                    *messages
                ]
            )
            return [response.choices[0].message.content]
        except Exception as e:
            print(f"Błąd podczas wyodrębniania zapytań: {e}")
            return []

    async def completion(self, messages: List[Dict[str, str]], model: str = "gpt-4", stream: bool = False) -> Dict[str, Any]:
        """
        Generuje odpowiedź na podstawie wiadomości.
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content
                    }
                }]
            }
        except Exception as e:
            print(f"Błąd podczas generowania odpowiedzi: {e}")
            return {
                "choices": [{
                    "message": {
                        "content": "Przepraszam, wystąpił błąd podczas generowania odpowiedzi."
                    }
                }]
            } 