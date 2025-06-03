import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Pobieranie konfiguracji z .env
CENTRAL_API_KEY = os.getenv('CENTRAL_API_KEY')
CENTRAL_API_URL = os.getenv('CENTRAL_API_URL')
FINE_TUNED_MODEL = os.getenv('FINE_TUNED_MODEL')

def verify_data():
    # Wczytanie danych do weryfikacji
    with open('verify.txt', 'r', encoding='utf-8') as f:
        verify_lines = f.readlines()

    correct_ids = []
    
    # Weryfikacja każdej linii
    for line in verify_lines:
        line = line.strip()
        if not line:
            continue
            
        # Przygotowanie zapytania w formacie zgodnym z danymi treningowymi
        messages = [
            {"role": "system", "content": "validate data"},
            {"role": "user", "content": line}
        ]
        
        # Wysłanie zapytania do modelu
        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=messages,
            temperature=0
        )
        
        # Sprawdzenie odpowiedzi
        result = response.choices[0].message.content.strip()
        print(f"Linia: {line} -> Odpowiedź modelu: {result}")
        
        if result == "1":
            # Wyciągnięcie ID z linii (pierwsze dwie cyfry przed znakiem =)
            data_id = line.split('=')[0].strip()
            # Upewniamy się, że ID jest dwucyfrową liczbą
            if data_id.isdigit() and len(data_id) == 2:
                correct_ids.append(data_id)

    # Sortowanie ID
    correct_ids.sort()

    # Przygotowanie raportu
    report = {
        "task": "research",
        "apikey": CENTRAL_API_KEY,
        "answer": correct_ids
    }
    
    print("\nWysyłany raport:", json.dumps(report, indent=2))
    
    # Wysłanie raportu do centrali
    response = requests.post(
        CENTRAL_API_URL,
        json=report
    )
    
    print(f"Status odpowiedzi: {response.status_code}")
    print(f"Treść odpowiedzi: {response.text}")

if __name__ == "__main__":
    verify_data() 