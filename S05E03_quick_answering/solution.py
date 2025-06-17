import json
import time
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio
import aiohttp
import logging
from datetime import datetime
import pathlib
import ast
from functools import lru_cache
import hashlib

# --- Konfiguracja ---
log_dir = pathlib.Path(__file__).parent / "logs"
results_dir = pathlib.Path(__file__).parent / "results"
log_dir.mkdir(exist_ok=True)
results_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"run_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Ładowanie zmiennych środowiskowych ---
load_dotenv()
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
PASSWORD = os.getenv('PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not all([API_KEY, BASE_URL, PASSWORD, OPENAI_API_KEY]):
    raise ValueError("Brak wymaganych zmiennych środowiskowych w pliku .env")

# --- Konfiguracja klientów ---
client_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Cache dla danych źródłowych
source_cache = {}

def get_cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

async def get_hash(session: aiohttp.ClientSession) -> str:
    async with session.post(BASE_URL, json={"password": PASSWORD}) as response:
        response.raise_for_status()
        data = await response.json()
        return data["message"]

async def get_tasks(session: aiohttp.ClientSession, hash_value: str) -> Dict[str, Any]:
    async with session.post(BASE_URL, json={"sign": hash_value}) as response:
        response.raise_for_status()
        tasks_data = await response.json()
        return tasks_data.get("message", tasks_data)

async def fetch_source_data(session: aiohttp.ClientSession, url: str) -> str:
    """Pobiera dane ze źródła z wykorzystaniem cache."""
    cache_key = get_cache_key(url)
    if cache_key in source_cache:
        return source_cache[cache_key]

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        async with session.get(url, headers=headers, timeout=1.5) as response:
            if response.status == 200:
                data = await response.text()
                source_cache[cache_key] = data
                return data
            return "BŁĄD: Nie udało się pobrać danych ze źródła."
    except Exception:
        return "BŁĄD: Nie udało się pobrać danych ze źródła."

async def solve_challenge_with_ai(session: aiohttp.ClientSession, url: str) -> List[str]:
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            task_definition = await response.json()
        
        questions_text = task_definition["task"]
        context_data = task_definition["data"]

        if isinstance(context_data, str) and context_data.startswith('http'):
            context_data = await fetch_source_data(session, context_data)

        if "Źródło wiedzy" in questions_text:
            source_url = questions_text.split("Źródło wiedzy ")[1].strip()
            questions = context_data
            context_data = await fetch_source_data(session, source_url)
            questions_text = "\n".join(questions)

        system_prompt = "Jesteś precyzyjnym systemem do odpowiadania na pytania. Dla każdego pytania w tekście, zwróć możliwie najkrótszą, poprawną odpowiedź, bez powtarzania pytania. Sformatuj wszystkie odpowiedzi jako listę stringów w formacie JSON. Odpowiedzi muszą być w tej samej kolejności co pytania. Zwróć tylko i wyłącznie sam JSON. Jeśli kontekst to informacja o błędzie, zwróć pustą listę []."
        user_prompt = f"""
Przeanalizuj poniższy tekst i odpowiedz na wszystkie zawarte w nim pytania.
Tekst z pytaniami:
---
{questions_text}
---
Dodatkowy kontekst (jeśli potrzebny):
---
{context_data}
---
Zwróć wynik jako tablicę JSON. Każdy element tablicy to string zawierający WYŁĄCZNIE możliwie najkrótszą odpowiedź.
Przykład: jeśli pytania to "Jaki jest kolor nieba?" i "Stolica Polski?", wynikiem musi być JSON: ["niebieski", "Warszawa"]
"""
        
        response = await client_openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Używamy szybszego modelu
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=300,  # Zmniejszamy limit tokenów
            temperature=0.0
        )
        
        ai_response_text = response.choices[0].message.content.strip()

        try:
            if ai_response_text.startswith("```json"):
                ai_response_text = ai_response_text.strip("```json").strip("`").strip()
            
            answers = ast.literal_eval(ai_response_text)
            if not answers:
                retry_prompt = f"""
Odpowiedz na poniższe pytania. Zwróć odpowiedzi jako tablicę JSON.
Pytania:
{questions_text}

Kontekst:
{context_data}

Zwróć tablicę JSON z odpowiedziami. Przykład: ["odpowiedź1", "odpowiedź2"]
"""
                retry_response = await client_openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Zwróć tylko tablicę JSON z odpowiedziami."},
                        {"role": "user", "content": retry_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.0
                )
                retry_text = retry_response.choices[0].message.content.strip()
                if retry_text.startswith("```json"):
                    retry_text = retry_text.strip("```json").strip("`").strip()
                answers = ast.literal_eval(retry_text)
            
            return answers if isinstance(answers, list) else [str(answers)]
        except (ValueError, SyntaxError):
            return [ai_response_text]

    except Exception:
        return [f"Błąd krytyczny {url}"]

async def main_async():
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        try:
            hash_value = await get_hash(session)
            tasks_data = await get_tasks(session, hash_value)
            
            challenge_urls = tasks_data.get("challenges", [])
            if not challenge_urls:
                return

            challenge_coroutines = [solve_challenge_with_ai(session, url) for url in challenge_urls]
            results_nested = await asyncio.gather(*challenge_coroutines)
            
            final_answers = [answer for sublist in results_nested for answer in sublist]

            answer_payload = {
                "apikey": API_KEY,
                "timestamp": tasks_data["timestamp"],
                "signature": tasks_data["signature"],
                "answer": final_answers
            }
            
            async with session.post(BASE_URL, json=answer_payload) as response:
                final_response = await response.json()
                print(f"\nOdpowiedź serwera: {json.dumps(final_response, ensure_ascii=False, indent=2)}")

        except Exception as e:
            logger.error(f"Wystąpił nieoczekiwany błąd w main: {e}", exc_info=True)
        finally:
            execution_time = time.time() - start_time
            logger.info(f"Zakończono wykonanie zadania. Czas wykonania: {execution_time:.2f} sekund")

if __name__ == "__main__":
    asyncio.run(main_async())