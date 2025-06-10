import os
import json
import requests
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja
API_KEY = os.getenv('API_KEY')
BASE_URL = "https://c3ntrala.ag3nts.org"
GPS_LOGS_URL = f"{BASE_URL}/data/{API_KEY}/gps.txt"
GPS_QUESTION_URL = f"{BASE_URL}/data/{API_KEY}/gps_question.json"
REPORT_URL = f"{BASE_URL}/report"

def get_gps_logs():
    """Pobiera logi z agenta GPS"""
    response = requests.get(GPS_LOGS_URL)
    return response.text

def get_gps_question():
    """Pobiera pytanie od Centrali"""
    response = requests.get(GPS_QUESTION_URL)
    return response.json()

def query_people_api(name):
    """Wysyła zapytanie do API osób"""
    url = f"{BASE_URL}/people"
    payload = {
        "apikey": API_KEY,
        "query": name
    }
    response = requests.post(url, json=payload)
    return response.json()

def query_places_api(city):
    """Wysyła zapytanie do API miejsc"""
    url = f"{BASE_URL}/places"
    payload = {
        "apikey": API_KEY,
        "query": city
    }
    response = requests.post(url, json=payload)
    return response.json()

def query_database(query):
    """Wysyła zapytanie do bazy danych"""
    url = f"{BASE_URL}/apidb"
    payload = {
        "task": "database",
        "apikey": API_KEY,
        "query": query
    }
    response = requests.post(url, json=payload)
    return response.json()

def send_report(answer):
    """Wysyła raport do Centrali"""
    payload = {
        "task": "gps",
        "apikey": API_KEY,
        "answer": answer
    }
    response = requests.post(REPORT_URL, json=payload)
    return response.json()

def get_people_in_city(city):
    """Zwraca listę osób widzianych w danym mieście (API /places)"""
    data = query_places_api(city)
    log_to_file(f"Odpowiedź z API /places dla {city}: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # Sprawdź różne formaty odpowiedzi
    if isinstance(data, dict):
        if "message" in data:
            # Jeśli mamy listę osób w message, rozdziel ją
            message = data["message"]
            if isinstance(message, str):
                # Usuń linki i inne niepotrzebne dane
                if "http" not in message.lower():
                    return [name.strip() for name in message.split() if name.strip()]
        elif "people" in data:
            return data["people"]
        elif "users" in data:
            return data["users"]
        elif "data" in data:
            return data["data"]
    elif isinstance(data, list):
        return data
    return []

def get_user_id(name):
    """Zwraca ID użytkownika z bazy danych lub None jeśli nie istnieje"""
    # Używamy username zamiast name, zgodnie ze strukturą bazy
    queries = [
        f"SELECT id FROM users WHERE username='{name}'",
        f"SELECT id FROM users WHERE LOWER(username)=LOWER('{name}')",
        f"SELECT id FROM users WHERE username LIKE '%{name}%'"
    ]
    
    for query in queries:
        data = query_database(query)
        log_to_file(f"Wynik zapytania '{query}': {json.dumps(data, indent=2, ensure_ascii=False)}")
        if isinstance(data, dict):
            if "reply" in data and data["reply"]:
                return data["reply"][0].get("id")
    return None

def get_gps_by_user_id(user_id):
    """Zwraca współrzędne GPS użytkownika po ID (API /gps)"""
    # Najpierw spróbujmy zapytania z query, jak w logach agenta
    try:
        url = f"{BASE_URL}/gps"
        payload = {"query": user_id}
        response = requests.post(url, json=payload)
        data = response.json()
        log_to_file(f"Odpowiedź z API /gps dla query={user_id}: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if isinstance(data, dict):
            if "message" in data and isinstance(data["message"], dict):
                if "lat" in data["message"] and "lon" in data["message"]:
                    return data["message"]
            elif "lat" in data and "lon" in data:
                return data
    except Exception as e:
        log_to_file(f"Błąd przy zapytaniu do /gps z query: {str(e)}")

    # Jeśli nie zadziałało, spróbujmy z userID
    try:
        payload = {"userID": user_id}
        response = requests.post(url, json=payload)
        data = response.json()
        log_to_file(f"Odpowiedź z API /gps dla userID={user_id}: {json.dumps(data, indent=2, ensure_ascii=False)}")
        if isinstance(data, dict):
            if "message" in data and isinstance(data["message"], dict):
                if "lat" in data["message"] and "lon" in data["message"]:
                    return data["message"]
            elif "lat" in data and "lon" in data:
                return data
    except Exception as e:
        log_to_file(f"Błąd przy zapytaniu do /gps z userID: {str(e)}")
    
    return None

def log_to_file(message):
    """Zapisuje wiadomość do pliku wyników i wyświetla w konsoli"""
    print(message)  # Wyświetl w konsoli
    with open("wyniki.txt", "a", encoding="utf-8") as f:
        f.write(f"{message}\n")

def main():
    # Wyczyść plik wyników na starcie
    with open("wyniki.txt", "w", encoding="utf-8") as f:
        f.write("=== Rozpoczęcie działania agenta ===\n\n")
    
    # Pobierz logi i pytanie
    logs = get_gps_logs()
    question = get_gps_question()
    
    log_to_file("--- LOGI AGENDA ---")
    log_to_file(logs)
    log_to_file("\n--- PYTANIE OD CENTRALI ---")
    log_to_file(question.get("question", ""))

    # 1. Pobierz osoby widziane w Lubawie
    osoby = get_people_in_city("Lubawa")
    log_to_file(f"\nOsoby widziane w Lubawie: {osoby}")

    # Usuń duplikaty i puste wartości
    osoby = list(set([o for o in osoby if o and o.strip()]))
    log_to_file(f"\nLista wszystkich znalezionych osób: {osoby}")

    # 2. Sprawdź każdą osobę w bazie, pomiń Barbarę
    odpowiedz = {}
    for osoba in osoby:
        if osoba.lower() == "barbara":
            log_to_file(f"Pomijam Barbarę - nie wolno pytać o jej lokalizację")
            continue
            
        # Najpierw spróbujmy bezpośrednio zapytania o GPS
        try:
            url = f"{BASE_URL}/gps"
            payload = {"query": osoba}
            response = requests.post(url, json=payload)
            data = response.json()
            log_to_file(f"Próba bezpośredniego zapytania GPS dla {osoba}: {json.dumps(data, indent=2, ensure_ascii=False)}")
            if isinstance(data, dict):
                if "message" in data and isinstance(data["message"], dict):
                    if "lat" in data["message"] and "lon" in data["message"]:
                        odpowiedz[osoba] = {"lat": data["message"]["lat"], "lon": data["message"]["lon"]}
                        continue
                elif "lat" in data and "lon" in data:
                    odpowiedz[osoba] = {"lat": data["lat"], "lon": data["lon"]}
                    continue
        except Exception as e:
            log_to_file(f"Błąd przy bezpośrednim zapytaniu GPS: {str(e)}")

        # Jeśli bezpośrednie zapytanie nie zadziałało, spróbujmy przez bazę danych
        user_id = get_user_id(osoba)
        if user_id is None:
            log_to_file(f"Pomijam {osoba} - nie znaleziono w bazie danych")
            continue
        log_to_file(f"Znaleziono {osoba} w bazie (ID: {user_id})")
        
        # Pobierz współrzędne GPS
        gps = get_gps_by_user_id(user_id)
        if gps and "lat" in gps and "lon" in gps:
            odpowiedz[osoba] = {"lat": gps["lat"], "lon": gps["lon"]}
            log_to_file(f"Pobrano GPS dla {osoba}: {gps}")
        else:
            log_to_file(f"Nie udało się pobrać GPS dla {osoba}")

    log_to_file(f"\nPrzygotowana odpowiedź do centrali:")
    log_to_file(json.dumps(odpowiedz, indent=2, ensure_ascii=False))

    # 4. Wyślij odpowiedź do centrali
    result = send_report(odpowiedz)
    log_to_file(f"\nOdpowiedź centrali: {result}")
    log_to_file("\n=== Zakończenie działania agenta ===")

if __name__ == "__main__":
    main() 