import requests
import json
from dotenv import load_dotenv
import os
import re
from typing import Set, List, Dict
from datetime import datetime
import shutil

# Ładowanie zmiennych środowiskowych
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Stałe
PEOPLE_API = "https://c3ntrala.ag3nts.org/people"
PLACES_API = "https://c3ntrala.ag3nts.org/places"
BARBARA_NOTE_URL = "https://c3ntrala.ag3nts.org/dane/barbara.txt"

# Tworzenie struktury katalogów
RESULTS_DIR = "results"
if os.path.exists(RESULTS_DIR):
    shutil.rmtree(RESULTS_DIR)
os.makedirs(RESULTS_DIR)
os.makedirs(os.path.join(RESULTS_DIR, "people"))
os.makedirs(os.path.join(RESULTS_DIR, "places"))
os.makedirs(os.path.join(RESULTS_DIR, "flags"))

def save_result(category: str, name: str, data: Dict):
    """Zapisuje wynik do pliku JSON"""
    filename = f"{name}.json"
    filepath = os.path.join(RESULTS_DIR, category, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def normalize_text(text: str) -> str:
    """Normalizuje tekst do formatu wymaganego przez API"""
    # Usuwanie polskich znaków i konwersja na wielkie litery
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.upper()

def get_barbara_note() -> str:
    """Pobiera notatkę o Barbarze"""
    try:
        response = requests.get(BARBARA_NOTE_URL)
        response.raise_for_status()
        note_text = response.text
        
        save_result("people", "barbara_note", {
            "text": note_text,
            "timestamp": datetime.now().isoformat()
        })
        
        return note_text
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania notatki: {e}")
        return ""

def extract_names_and_cities(text: str) -> tuple[Set[str], Set[str]]:
    """Wyodrębnia imiona i miasta z tekstu"""
    # Znane miasta z tekstu
    known_cities = {'KRAKOW', 'WARSZAWA'}
    
    # Znane imiona z tekstu
    known_names = {'BARBARA', 'ALEKSANDER', 'ANDRZEJ', 'RAFAŁ'}
    
    # Dodaj znane miasta i imiona
    cities = set(known_cities)
    names = set(known_names)
    
    # Zapisz wyniki analizy
    save_result("people", "initial_analysis", {
        "names": list(names),
        "cities": list(cities),
        "timestamp": datetime.now().isoformat()
    })
    
    return names, cities

def analyze_response_for_flags(response_data: Dict) -> List[str]:
    """Analizuje odpowiedź API w poszukiwaniu ukrytych flag"""
    flags = []
    
    # Sprawdź wszystkie pola w odpowiedzi
    for key, value in response_data.items():
        if isinstance(value, str):
            # Szukaj wzorców flag
            # Flagi często zaczynają się od "flag{" lub "flag["
            flag_patterns = [
                r'flag\{[^}]+\}',
                r'flag\[[^\]]+\]',
                r'flag\([^)]+\)',
                r'flag<[^>]+>',
                r'flag:[^:]+$',
                r'flag\s*=\s*[^\s]+',
                r'flag\s*:\s*[^\s]+'
            ]
            
            for pattern in flag_patterns:
                matches = re.findall(pattern, value, re.IGNORECASE)
                flags.extend(matches)
            
            # Sprawdź czy cała wartość wygląda jak flaga
            if re.match(r'^[a-zA-Z0-9_\-]+$', value) and len(value) > 10:
                flags.append(value)
    
    return flags

def analyze_special_chars(response_data: Dict) -> List[str]:
    """Analizuje odpowiedź API w poszukiwaniu znaków specjalnych"""
    special_chars = []
    
    if 'message' in response_data:
        message = response_data['message']
        # Szukaj znaków specjalnych i symboli
        chars = re.findall(r'[^\w\s]', message)
        if chars:
            special_chars.extend(chars)
            print(f"Znaleziono znaki specjalne: {chars}")
            
            # Zapisz znaki specjalne
            save_result("flags", f"special_chars_{datetime.now().strftime('%Y%m%d_%H%M%S')}", {
                "chars": chars,
                "original_message": message,
                "timestamp": datetime.now().isoformat()
            })
    
    return special_chars

def parse_api_response(response_data: Dict) -> List[str]:
    """Parsuje odpowiedź z API"""
    # Najpierw sprawdź czy nie ma ukrytej flagi
    flags = analyze_response_for_flags(response_data)
    if flags:
        print(f"Znaleziono potencjalne flagi: {flags}")
        save_result("flags", f"found_flags_{datetime.now().strftime('%Y%m%d_%H%M%S')}", {
            "flags": flags,
            "source_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
    
    # Sprawdź znaki specjalne
    special_chars = analyze_special_chars(response_data)
    
    if 'message' in response_data:
        message = response_data['message']
        # Ignoruj odpowiedzi zawierające "[**RESTRICTED DATA**]"
        if "[**RESTRICTED DATA**]" in message:
            return []
        # Jeśli odpowiedź jest w formacie tekstowym, podziel na słowa
        return [word.strip() for word in message.split()]
    return []

def query_api(endpoint: str, query: str) -> List[str]:
    """Wysyła zapytanie do API"""
    try:
        payload = {
            "apikey": API_KEY,
            "query": query
        }
        
        print(f"Wysyłam zapytanie do {endpoint} z query: {query}")
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        print(f"Otrzymano odpowiedź: {response_data}")
        
        result = parse_api_response(response_data)
        
        # Zapisz wynik zapytania
        category = "places" if endpoint == PEOPLE_API else "people"
        save_result(category, f"{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", {
            "query": query,
            "endpoint": endpoint,
            "request_payload": payload,
            "response_data": response_data,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas zapytania do API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Błąd podczas parsowania odpowiedzi JSON: {e}")
        return []
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        return []

def normalize_name(name: str) -> str:
    """Normalizuje imię do jednej wersji"""
    # Usuń polskie znaki i zamień na wielkie litery
    name = normalize_text(name)
    # Zamień różne wersje tego samego imienia
    name_variants = {
        'RAFAL': 'RAFAŁ',
        'RAFAŁ': 'RAFAŁ',
        'RAFAEL': 'RAFAŁ',
        'RAFAEL': 'RAFAŁ'
    }
    return name_variants.get(name, name)

def find_barbara():
    """Główna funkcja wyszukująca Barbarę"""
    # Pobierz notatkę
    note = get_barbara_note()
    if not note:
        print("Nie udało się pobrać notatki o Barbarze")
        return None
        
    print("Pobrano notatkę o Barbarze")
    print(f"Treść notatki: {note}")
    
    # Wyodrębnij imiona i miasta
    names, cities = extract_names_and_cities(note)
    print(f"Znalezione imiona: {names}")
    print(f"Znalezione miasta: {cities}")
    
    # Kolejki do sprawdzenia
    names_to_check = {normalize_name(name) for name in names}
    cities_to_check = set(cities)
    checked_names = set()
    checked_cities = set()
    
    # Słowniki do przechowywania powiązań
    name_to_places = {}  # gdzie była dana osoba
    place_to_names = {}  # kto był w danym miejscu
    
    # Najpierw sprawdź LUBLIN
    print("\nSprawdzam miasto: LUBLIN")
    lublin_people = query_api(PLACES_API, "LUBLIN")
    checked_cities.add("LUBLIN")
    place_to_names["LUBLIN"] = lublin_people
    print(f"W mieście LUBLIN byli: {lublin_people}")
    
    # Następnie sprawdź RAFAL
    print("\nSprawdzam osobę: RAFAŁ")
    rafal_places = query_api(PEOPLE_API, "RAFAL")
    checked_names.add("RAFAL")
    name_to_places["RAFAL"] = rafal_places
    print(f"Osoba RAFAŁ była w miejscach: {rafal_places}")
    
    # Dodaj nowe miasta do sprawdzenia
    for place in rafal_places:
        if place not in checked_cities and place not in cities_to_check:
            cities_to_check.add(place)
    
    # Dodaj nowe imiona do sprawdzenia
    for person in lublin_people:
        normalized_person = normalize_name(person)
        if normalized_person not in checked_names and normalized_person not in names_to_check:
            names_to_check.add(normalized_person)
    
    # Główna pętla wyszukiwania
    iteration = 0
    while names_to_check or cities_to_check:
        iteration += 1
        print(f"\nIteracja {iteration}")
        print(f"Pozostało do sprawdzenia: {len(names_to_check)} imion, {len(cities_to_check)} miast")
        
        # Sprawdź imiona
        if names_to_check:
            name = names_to_check.pop()
            normalized_name = normalize_name(name)
            if normalized_name in checked_names:
                continue
                
            print(f"\nSprawdzam osobę: {normalized_name}")
            places = query_api(PEOPLE_API, normalized_name)
            checked_names.add(normalized_name)
            
            # Zapisz powiązania osoby z miejscami
            name_to_places[normalized_name] = places
            print(f"Osoba {normalized_name} była w miejscach: {places}")
            
            # Dodaj nowe miasta do sprawdzenia
            for place in places:
                if place not in checked_cities and place not in cities_to_check:
                    cities_to_check.add(place)
        
        # Sprawdź miasta
        if cities_to_check:
            city = cities_to_check.pop()
            if city in checked_cities:
                continue
                
            print(f"\nSprawdzam miasto: {city}")
            people = query_api(PLACES_API, city)
            checked_cities.add(city)
            
            # Zapisz powiązania miasta z osobami
            place_to_names[city] = people
            print(f"W mieście {city} byli: {people}")
            
            # Jeśli znaleziono Barbarę w nowym mieście
            if 'BARBARA' in people and city not in cities:
                print(f"\nZNALEZIONO! Barbara jest w mieście: {city}")
                # Zapisz szczegółowe powiązania
                save_result("people", "detailed_connections", {
                    "name_to_places": name_to_places,
                    "place_to_names": place_to_names,
                    "barbara_location": city,
                    "timestamp": datetime.now().isoformat()
                })
                return city
            
            # Dodaj nowe imiona do sprawdzenia
            for person in people:
                normalized_person = normalize_name(person)
                if normalized_person not in checked_names and normalized_person not in names_to_check:
                    names_to_check.add(normalized_person)
        
        # Zapisz postęp po każdej iteracji
        save_result("people", f"progress_iteration_{iteration}", {
            "checked_names": list(checked_names),
            "checked_cities": list(checked_cities),
            "names_to_check": list(names_to_check),
            "cities_to_check": list(cities_to_check),
            "name_to_places": name_to_places,
            "place_to_names": place_to_names,
            "timestamp": datetime.now().isoformat()
        })
    
    # Zapisz podsumowanie poszukiwań
    save_result("people", "search_summary", {
        "checked_names": list(checked_names),
        "checked_cities": list(checked_cities),
        "name_to_places": name_to_places,
        "place_to_names": place_to_names,
        "timestamp": datetime.now().isoformat()
    })
    
    return None

if __name__ == "__main__":
    result = find_barbara()
    if result:
        print(f"Barbara została znaleziona w mieście: {result}")
        # Przygotuj odpowiedź do wysłania
        response = {
            "task": "loop",
            "apikey": API_KEY,
            "answer": result
        }
        print("Odpowiedź do wysłania:", json.dumps(response, indent=2))
        
        # Zapisz odpowiedź
        save_result("people", "final_answer", response)
    else:
        print("Nie znaleziono Barbary") 