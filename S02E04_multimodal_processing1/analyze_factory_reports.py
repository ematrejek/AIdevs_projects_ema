import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import whisper
from PIL import Image
import base64
from io import BytesIO
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Załaduj zmienne środowiskowe
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Brak klucza API OpenAI w pliku .env")

api_url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def analyze_text_file(file_path):
    """Analizuje plik tekstowy i zwraca kategorię."""
    logger.info(f"Analizuję plik tekstowy: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    prompt = f"""Przeanalizuj poniższy tekst i zaklasyfikuj go do jednej z kategorii:
    - people: Uwzględniaj tylko notatki zawierające informacje o SCHWYTANYCH LUDZIACH lub o ŚLADACH ICH OBECNOŚCI.
    - hardware: Usterki hardwarowe (nie software) - tylko jeśli notatki zawierają informacje o USTERKACH w HARDWARE.
    - w przeciwnym razie zwróć none
    
    Tekst: {content}
    
    Odpowiedz tylko jedną kategorią: people, hardware lub none.
    Pamiętaj:
    - Kategoria "hardware" powinna być używana WYŁĄCZNIE dla USTEREK HARDWARE"""
    
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        category = response.json()["choices"][0]["message"]["content"].strip().lower()
        logger.info(f"Kategoria dla {file_path}: {category}")
        return category
    except Exception as e:
        logger.error(f"Błąd podczas analizy pliku {file_path}: {str(e)}")
        return "none"

def encode_image_to_base64(image_path):
    """Konwertuje obraz do formatu base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_file(file_path):
    """Analizuje plik obrazu i zwraca kategorię."""
    logger.info(f"Analizuję plik obrazu: {file_path}")
    base64_image = encode_image_to_base64(file_path)
    
    prompt = """Przeanalizuj poniższy obraz i zaklasyfikuj go do jednej z kategorii:
    - people: Uwzględniaj tylko notatki zawierające informacje o SCHWYTANYCH LUDZIACH lub o ŚLADACH ICH OBECNOŚCI.
    - hardware: Usterki hardwarowe (nie software) - tylko jeśli notatki zawierają informacje o USTERKACH w HARDWARE.
    - w przeciwnym razie zwróć none
    
    Odpowiedz tylko jedną kategorią: people, hardware lub none."""
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        category = response.json()["choices"][0]["message"]["content"].strip().lower()
        logger.info(f"Kategoria dla {file_path}: {category}")
        return category
    except Exception as e:
        logger.error(f"Błąd podczas analizy pliku {file_path}: {str(e)}")
        return "none"

def analyze_audio_file(file_path):
    """Analizuje plik audio i zwraca kategorię."""
    logger.info(f"Analizuję plik audio: {file_path}")
    try:
        # Konwertujemy na obiekt Path jeśli nie jest
        file_path = Path(file_path)
        logger.info(f"Pełna ścieżka do pliku audio: {file_path.absolute()}")
        
        if not file_path.exists():
            logger.error(f"Plik audio nie istnieje: {file_path}")
            return "none"
            
        logger.info(f"Ładowanie modelu Whisper...")
        model = whisper.load_model("base")
        logger.info(f"Transkrybuję plik audio: {file_path}")
        result = model.transcribe(str(file_path))
        text = result["text"]
        logger.info(f"Transkrypcja: {text}")
        
        prompt = f"""Przeanalizuj poniższy tekst z transkrypcji audio i zaklasyfikuj go do jednej z kategorii:
        - people: Uwzględniaj tylko notatki zawierające informacje o SCHWYTANYCH LUDZIACH lub o ŚLADACH ICH OBECNOŚCI.
        - hardware: Usterki hardwarowe (nie software) - tylko jeśli notatki zawierają informacje o USTERKACH w HARDWARE.
        - w przeciwnym razie zwróć none
        
        Tekst: {text}
        
        Odpowiedz tylko jedną kategorią: people, hardware lub none."""
        
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        category = response.json()["choices"][0]["message"]["content"].strip().lower()
        logger.info(f"Kategoria dla {file_path}: {category}")
        return category
    except Exception as e:
        logger.error(f"Błąd podczas analizy pliku {file_path}: {str(e)}")
        return "none"

def analyze_factory_reports():
    """Główna funkcja analizująca raporty z fabryki."""
    reports_dir = Path(".")
    categories = {
        "people": [],
        "hardware": [],
        "none": []  # Dodajemy kategorię "none"
    }
    
    excluded = {"facts", "weapons_tests.zip", "report.json", "requirements.txt", "analyze_factory_reports.py", ".env", "venv", "send_report.py"}
    
    logger.info(f"Szukam plików w katalogu: {reports_dir.absolute()}")
    
    # Analizujemy tylko pliki, które nie są w kategoriach "people" i "hardware"
    for file_path in reports_dir.glob("*"):
        if file_path.name in excluded or file_path.is_dir():
            logger.info(f"Pomijam: {file_path.name}")
            continue
            
        if file_path.name in categories["people"] or file_path.name in categories["hardware"]:
            logger.info(f"Pomijam plik z kategorii 'people' lub 'hardware': {file_path.name}")
            continue
            
        logger.info(f"Znaleziono plik: {file_path.name}")
        
        try:
            if file_path.suffix.lower() == '.txt':
                category = analyze_text_file(file_path)
            elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                category = analyze_image_file(file_path)
            elif file_path.suffix.lower() in ['.mp3', '.wav']:
                if not file_path.exists():
                    logger.error(f"Plik audio nie istnieje: {file_path}")
                    categories["none"].append(file_path.name)
                    continue
                category = analyze_audio_file(file_path)
            else:
                continue
                
            if category in categories:
                categories[category].append(file_path.name)
                logger.info(f"Dodano {file_path.name} do kategorii {category}")
            else:
                logger.warning(f"Nieznana kategoria: {category}, ustawiam jako 'none'")
                categories["none"].append(file_path.name)
                
        except Exception as e:
            logger.error(f"Błąd podczas analizy pliku {file_path.name}: {str(e)}")
            categories["none"].append(file_path.name)
            continue
    
    # Usuwamy kategorię "none" z raportu przed wysłaniem
    if "none" in categories:
        del categories["none"]
    
    # Sortowanie nazw plików alfabetycznie
    for category in categories:
        categories[category].sort()
    
    # Przygotowanie raportu
    report = {
        "task": "kategorie",
        "apikey": "8eed1983-ee32-479e-8c44-eb85077a62e8",
        "answer": categories
    }
    
    logger.info("\nPrzygotowany raport:")
    logger.info(json.dumps(report, indent=2, ensure_ascii=False))
    
    # Wysłanie raportu
    try:
        response = requests.post(
            "https://c3ntrala.ag3nts.org/report",
            json=report,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        response.raise_for_status()
        logger.info("\nRaport został pomyślnie wysłany!")
        logger.info(f"Odpowiedź serwera: {response.text}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            logger.error(f"\nBłąd 400 podczas wysyłania raportu. Treść odpowiedzi:")
            logger.error(f"Status: {e.response.status_code}")
            logger.error(f"Headers: {e.response.headers}")
            logger.error(f"Body: {e.response.text}")
        else:
            logger.error(f"\nBłąd podczas wysyłania raportu: {str(e)}")
        # Zapisanie raportu do pliku w przypadku błędu
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info("Raport został zapisany do pliku report.json")
    except Exception as e:
        logger.error(f"\nBłąd podczas wysyłania raportu: {str(e)}")
        # Zapisanie raportu do pliku w przypadku błędu
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info("Raport został zapisany do pliku report.json")

if __name__ == "__main__":
    analyze_factory_reports()