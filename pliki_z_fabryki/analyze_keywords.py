import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
import logging
import random

# --- Konfiguracja ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Brak klucza API OpenAI w pliku .env")

REPORT_API_KEY = "8eed1983-ee32-479e-8c44-eb85077a62e8" # Zastąp swoim kluczem API

API_URL = "https://api.openai.com/v1/chat/completions"
REPORT_URL = "https://c3ntrala.ag3nts.org/report"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
MODEL = "gpt-4o"  # Możesz spróbować "gpt-4o-mini" lub "gpt-3.5-turbo"
CACHE_DIR = Path("cache")
KEYWORDS_DIR = CACHE_DIR / "keywords"

# Utwórz foldery cache, jeśli nie istnieją
CACHE_DIR.mkdir(exist_ok=True)
KEYWORDS_DIR.mkdir(exist_ok=True)

# --- Funkcje Pomocnicze ---

def read_files(directory: Path, pattern: str) -> dict[str, str]:
    """Wczytuje pliki pasujące do wzorca z danego katalogu."""
    data = {}
    if not directory.is_dir():
        logger.warning(f"Folder '{directory}' nie istnieje w {Path.cwd()}. Zwracam pusty słownik.")
        return data
        
    for file_path in directory.glob(pattern):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data[file_path.name] = f.read().strip()
            logger.info(f"Wczytano plik: {file_path.name}")
        except Exception as e:
            logger.error(f"Nie udało się wczytać pliku {file_path.name}: {e}")
            
    return data

def make_api_call(payload, step_name, expect_json=False):
    """Wykonuje wywołanie API OpenAI z obsługą błędów i ponowieniami."""
    max_retries = 5
    base_delay = 15

    for attempt in range(max_retries):
        try:
            logger.debug(f"Próba {attempt + 1}/{max_retries} dla kroku '{step_name}'...")
            if expect_json:
                payload["response_format"] = { "type": "json_object" }

            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and data["choices"]:
                content = data["choices"][0]["message"]["content"].strip()
                logger.debug(f"Otrzymano odpowiedź dla '{step_name}'.")
                
                if expect_json:
                    try:
                        # Czasem AI otacza JSON w ```json ... ```, usuwamy to
                        if content.startswith("```json"):
                            content = content.strip("```json").strip("`").strip()
                        return json.loads(content)
                    except json.JSONDecodeError as json_err:
                        logger.error(f"Błąd parsowania JSON w kroku '{step_name}'. Odpowiedź: {content}. Błąd: {json_err}")
                        return None
                else:
                    return content # Zwróć string
            else:
                logger.error(f"Nieprawidłowa odpowiedź API dla '{step_name}': {data}")
                return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt < max_retries - 1:
                    retry_after = e.response.headers.get('retry-after')
                    wait_time = base_delay * (2 ** attempt) + random.uniform(1, 5)
                    if retry_after and retry_after.isdigit():
                       wait_time = int(retry_after) + 2
                    logger.warning(f"Błąd 429 ({step_name}). Czekam {wait_time:.2f}s...")
                    time.sleep(wait_time)
                    continue
            logger.error(f"Błąd HTTP w kroku '{step_name}': {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd sieciowy w kroku '{step_name}': {e}")
            if attempt < max_retries - 1:
                 wait_time = base_delay * (2 ** attempt) + random.uniform(1, 5)
                 logger.warning(f"Czekam {wait_time:.2f}s przed ponowieniem...")
                 time.sleep(wait_time)
                 continue
            return None
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd w kroku '{step_name}': {e}")
            return None

    logger.error(f"Nie udało się wykonać zapytania w kroku '{step_name}' po {max_retries} próbach.")
    return None

def extract_person_facts(facts: dict[str, str]) -> dict[str, list[str]]:
    """Wyciąga osoby i ich atrybuty z faktów używając AI."""
    person_map = {}
    wait_between_calls = 5 # Pauza między analizą faktów

    logger.info("Rozpoczynam ekstrakcję osób z faktów...")
    for fact_name, fact_content in facts.items():
        prompt = f"""Przeanalizuj poniższy tekst i znajdź wszystkie wymienione osoby. Dla każdej osoby, wypisz jej imię i nazwisko oraz wszystkie powiązane z nią fakty, cechy lub role (np. zawód, umiejętność, status).

Tekst:
{fact_content}

Zwróć odpowiedź w formacie JSON jako listę obiektów, gdzie każdy obiekt ma klucz 'imie_nazwisko' i 'atrybuty' (lista stringów). Jeśli nie ma osób, zwróć pustą listę.
Przykład:
{{
  "osoby": [
    {{"imie_nazwisko": "Jan Kowalski", "atrybuty": ["nauczyciel", "programista", "Kraków"]}},
    {{"imie_nazwisko": "Anna Nowak", "atrybuty": ["inżynier", "ruch oporu"]}}
  ]
}}
"""
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        }
        
        analysis = make_api_call(payload, f"extract_person_facts ({fact_name})", expect_json=True)
        
        if analysis and "osoby" in analysis and isinstance(analysis["osoby"], list):
            for person_data in analysis["osoby"]:
                name = person_data.get("imie_nazwisko")
                attributes = person_data.get("atrybuty", [])
                if name:
                    name_lower = name.lower()
                    if name_lower not in person_map:
                        person_map[name_lower] = []
                    person_map[name_lower].extend(attributes)
                    person_map[name_lower] = list(set(person_map[name_lower])) # Usuń duplikaty
            logger.info(f"Wyciągnięto osoby z faktu: {fact_name}")
        else:
            logger.warning(f"Nie udało się wyciągnąć osób z faktu {fact_name}.")
            
        time.sleep(wait_between_calls)

    return person_map

def load_or_create_person_map(facts: dict[str, str]) -> dict[str, list[str]]:
    """Wczytuje mapę osób z cache lub tworzy ją."""
    cache_file = CACHE_DIR / "persons.json"
    if cache_file.exists():
        logger.info("Wczytuję mapę osób z cache...")
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Błąd wczytywania cache osób: {e}. Tworzę na nowo.")
            
    person_map = extract_person_facts(facts)
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(person_map, f, ensure_ascii=False, indent=2)
        logger.info("Zapisano mapę osób do cache.")
    except Exception as e:
        logger.error(f"Nie udało się zapisać cache osób: {e}")
        
    return person_map

def find_relevant_facts(report_content: str, facts: dict[str, str], person_map: dict[str, list[str]]) -> dict[str, str]:
    """Wybiera fakty powiązane z raportem (prosta metoda)."""
    relevant_facts = {}
    report_lower = report_content.lower()

    # Szukaj osób z mapy osób w raporcie
    for person_name_lower in person_map.keys():
        if person_name_lower in report_lower:
            # Jeśli osoba jest w raporcie, znajdź wszystkie fakty, które o niej mówią
            for fact_name, fact_content in facts.items():
                if person_name_lower in fact_content.lower():
                    relevant_facts[fact_name] = fact_content

    # Można dodać więcej logiki (np. szukanie sektorów, kluczowych słów)
    # Na razie, jeśli nie znaleziono osób, zwrócimy wszystkie fakty (bezpieczniejsze niż nic)
    if not relevant_facts:
        logger.warning(f"Nie znaleziono bezpośrednich powiązań osób, używam wszystkich faktów.")
        return facts

    logger.info(f"Wybrano {len(relevant_facts)} powiązanych faktów.")
    return relevant_facts


def generate_keywords(report_content, relevant_facts, person_map, report_filename):
    """Generuje słowa kluczowe używając AI."""
    
    sector = "Nieznany"
    try:
        sector_part = Path(report_filename).stem.split('-')[-1] # np. 'sektor_C4'
        sector = sector_part.split('_')[1] # np. 'C4'
    except Exception:
        logger.warning(f"Nie udało się wyodrębnić sektora z nazwy pliku: {report_filename}")

    prompt = f"""Przeanalizuj poniższy raport, powiązane fakty i informacje o osobach. Wygeneruj listę słów kluczowych w języku polskim.

--- RAPORT ({report_filename}) ---
Sektor: {sector}
Treść:
{report_content}
--- KONIEC RAPORTU ---

--- POWIĄZANE FAKTY ---
{json.dumps(relevant_facts, ensure_ascii=False, indent=2)}
--- KONIEC FAKTÓW ---

--- ZNANE OSOBY (mapa: imię -> atrybuty) ---
{json.dumps(person_map, ensure_ascii=False, indent=2)}
--- KONIEC OSÓB ---

--- ZADANIE ---
Wygeneruj listę słów kluczowych. BARDZO WAŻNE: Jeśli raport i fakty wskazują na schwytanie/aresztowanie nauczyciela (np. Aleksandra Ragowskiego), słowa kluczowe MUSZĄ zawierać "nauczyciel" i "schwytanie" (lub "aresztowanie"). Użyj informacji z faktów, aby wzbogacić opis (np. dodać zawód). Zawsze dodawaj sektor (np. `sektor_C4`).

--- WYMAGANIA DOTYCZĄCE SŁÓW KLUCZOWYCH ---
1. Język polski.
2. Forma: Mianownik liczby pojedynczej (np. "nauczyciel", "programista", "awaria", "schwytanie"). Używaj liczby mnogiej tylko, gdy to konieczne (np. 'roboty').
3. Format: Słowa oddzielone przecinkami, BEZ spacji (np. słowo1,słowo2,słowo3).
4. Precyzja: Dokładnie opisz raport, łącząc treść, FAKTY i nazwę pliku.
5. Kompletność: Uwzględnij *wszystkie* ważne informacje.
6. Unikalność: NIE powtarzaj tych samych słów kluczowych.

--- ODPOWIEDŹ ---
Zwróć TYLKO listę słów kluczowych oddzielonych przecinkami.
"""
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    keywords = make_api_call(payload, f"generate_keywords ({report_filename})")

    if keywords:
        unique_keywords = list(dict.fromkeys([k.strip().lower() for k in keywords.split(',') if k.strip()]))
        cleaned_keywords = ",".join(unique_keywords)
        logger.info(f"Oczyszczone słowa kluczowe dla {report_filename}: {cleaned_keywords[:150]}...")
        return cleaned_keywords
    else:
        logger.error(f"Nie udało się wygenerować słów kluczowych dla {report_filename}.")
        return ""

def replace_underscores_with_spaces(keywords_dict):
    """Zamienia podkreślniki na spacje w słowach kluczowych."""
    return {filename: keywords.replace('_', ' ') for filename, keywords in keywords_dict.items()}

# --- Główna Funkcja Orkiestracji ---

def analyze_factory_reports():
    """Główna funkcja analizująca raporty z fabryki."""
    reports_dir = Path(".")
    facts_dir = Path("fakty")
    
    reports = read_files(reports_dir, "2024-11-12_report-*.txt")
    facts = read_files(facts_dir, "*.txt")
    
    if not reports:
        logger.error("Nie znaleziono plików raportów. Zakończono.")
        return
        
    if not facts:
        logger.warning("Nie znaleziono plików faktów. Analiza będzie kontynuowana bez nich.")

    person_map = load_or_create_person_map(facts)
    answer = {}

    expected_count = 10 # Lub len(reports) jeśli ma być dynamicznie
    wait_between_reports = 15 # Zmniejszamy, bo mniej wywołań na raport

    for i, (filename, content) in enumerate(sorted(reports.items())):
        cache_file = KEYWORDS_DIR / f"{filename}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    answer[filename] = data['keywords']
                    logger.info(f"Wczytano słowa kluczowe z cache dla: {filename}")
                    continue # Przejdź do następnego pliku
            except Exception as e:
                logger.warning(f"Błąd wczytywania cache dla {filename}: {e}. Generuję na nowo.")

        logger.info(f"Przetwarzam raport: {filename} ({i + 1}/{len(reports)})")
        
        relevant_facts = find_relevant_facts(content, facts, person_map)
        
        keywords = generate_keywords(content, relevant_facts, person_map, filename)
        
        if keywords:
            answer[filename] = keywords
            # Zapisz do cache
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump({"keywords": keywords}, f, ensure_ascii=False, indent=2)
                logger.info(f"Zapisano słowa kluczowe do cache dla: {filename}")
            except Exception as e:
                logger.error(f"Nie udało się zapisać cache dla {filename}: {e}")
        else:
            logger.error(f"Nie udało się wygenerować słów kluczowych dla {filename}. PRZERYWAM PRACĘ.")
            return 
        
        if i + 1 < len(reports):
             logger.info(f"Oczekiwanie {wait_between_reports} sekund przed następnym raportem...")
             time.sleep(wait_between_reports)

    if len(answer) != expected_count:
        logger.error(f"Wygenerowano słowa kluczowe tylko dla {len(answer)} raportów, oczekiwano {expected_count}. Sprawdź logi.")
        return
    
    # Zamiana podkreślników na spacje przed wysłaniem
    answer = replace_underscores_with_spaces(answer)
    
    report_payload = {
        "task": "dokumenty",
        "apikey": REPORT_API_KEY,
        "answer": answer
    }
    
    logger.info("\n--- PRZYGOTOWANY RAPORT ---")
    logger.info(json.dumps(report_payload, indent=2, ensure_ascii=False))
    logger.info("--- KONIEC RAPORTU ---")

    with open("final_report.json", "w", encoding="utf-8") as f:
        json.dump(report_payload, f, ensure_ascii=False, indent=2)
    logger.info("Końcowy raport został zapisany do pliku final_report.json")

    logger.info(f"Wysyłanie raportu do: {REPORT_URL}")
    try:
        response = requests.post(
            REPORT_URL,
            json=report_payload,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        response.raise_for_status()
        logger.info("\nRaport został pomyślnie wysłany!")
        logger.info(f"Odpowiedź serwera: {response.text}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"\nBłąd HTTP podczas wysyłania raportu: {e.response.status_code}")
        logger.error(f"Odpowiedź serwera: {e.response.text}")
        logger.error("Raport NIE został wysłany. Sprawdź plik final_report.json i logi.")
    except Exception as e:
        logger.error(f"\nNieoczekiwany błąd podczas wysyłania raportu: {e}")
        logger.error("Raport NIE został wysłany. Sprawdź plik final_report.json i logi.")

# --- Uruchomienie ---
if __name__ == "__main__":
    analyze_factory_reports()