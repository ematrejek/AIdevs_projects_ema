import requests
import json
from datetime import datetime
import os

# Konfiguracja
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- WERSJA DLA TRYBU JUSTUPDATE ---
# Przygotowanie danych do wysłania z dodanym polem "justUpdate"
data = {
    "task": "serce",
    "apikey": API_KEY,
    "answer": WEBHOOK_URL,
    "justUpdate": True  # Ta linia pozwala ominąć testy i od razu przejść do rozmowy
}

# Utworzenie katalogu na odpowiedzi jeśli nie istnieje
responses_dir = "responses"
if not os.path.exists(responses_dir):
    os.makedirs(responses_dir)

# Nazwa pliku z odpowiedzią
# Zmieniono format, aby uniknąć konfliktów z ':' w nazwach plików na niektórych systemach
response_file = os.path.join(responses_dir, f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

try:
    print(f"Wysyłam zgłoszenie do centrali (tryb justUpdate)...")
    print(f"URL API: {WEBHOOK_URL}")
    
    # Wysłanie żądania
    response = requests.post(API_URL, json=data)
    
    # Zapisanie odpowiedzi do pliku
    # Używamy response.json() dla czytelniejszego formatu
    with open(response_file, "w", encoding="utf-8") as f:
        f.write(f"Status code: {response.status_code}\n")
        f.write(f"\nResponse body:\n")
        json.dump(response.json(), f, indent=4, ensure_ascii=False)
    
    print(f"\nOdpowiedź została zapisana do pliku: {response_file}")
    print(f"\nStatus code: {response.status_code}")
    print("Odpowiedź:")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

except Exception as e:
    print(f"Wystąpił błąd: {str(e)}")