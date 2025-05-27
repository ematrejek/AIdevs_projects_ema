import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIService:
    def __init__(self):
        # Ładuj zmienne środowiskowe z pliku .env
        load_dotenv()
        
        # Sprawdź czy klucz API istnieje
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Brak klucza OPENAI_API_KEY w pliku .env")
        
        # Inicjalizuj klienta OpenAI z kluczem z .env
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4"
    
    async def get_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

## async def - deklaracja funkcja asynchronicznej; pozwala na wykonywanie operacji bez blokowania wątku programu
## jest szczególnie przydatna w przypadku operacji I/O, takich jak łączenie z API, operacje na bazie danych ,plikach, zapytania sieciowe

## używamy asynchroniczności, bo zapytanie do API OpenAI może zająć kilka sekund
## bez asynchroniczności, program musiałby poczekać na odpowiedź, blokujac inne operacje
## z asynchronicznością można wykonywać inne operacje
## wykonujemy wiele zapytań do API (dla kazdego tekstu w kolekcji)
## każde zapytanie może zająć kilka sekund
## dzięki asynchroniczności, można wykonywać te zapytania równolegle
## dlatego w głównym pliku używamy asyncio.run(main()), aby uruchomić asynchroniczny kod w pętli
## z asynchronicznością mamy response = await; a bez by nie było await
