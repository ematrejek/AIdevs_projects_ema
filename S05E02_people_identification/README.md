# Zadanie S05E02 - Identyfikacja osób

## Opis zadania
Zadanie polega na odtworzeniu agenta, który analizuje logi i odpowiada na pytania Centrali dotyczące lokalizacji osób. Agent musi:
1. Przeanalizować logi z poprzedniego agenta
2. Wczytać pytanie od Centrali
3. Użyć dostępnych API do znalezienia informacji
4. Zwrócić odpowiedź w wymaganym formacie

## Wymagania
- Python 3.x
- Biblioteki: `requests`, `python-dotenv`

## Instalacja
1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Upewnij się, że masz plik `.env` z kluczem API:
```
API_KEY=twój-klucz-api
```

## Uruchomienie
```bash
python solution.py
```

## Struktura projektu
- `solution.py` - główny skrypt
- `requirements.txt` - lista zależności
- `.env` - plik z kluczem API
- `wyniki.txt` - plik z logami działania

## API
Skrypt korzysta z dwóch API:
1. API do bazy danych (`/apidb`)
   - Pozwala na wykonywanie zapytań SQL
   - Używane do sprawdzania ID użytkowników

2. API do lokalizacji (`/gps`)
   - Zwraca współrzędne GPS dla użytkowników
   - Wymaga ID użytkownika

## Format odpowiedzi
Odpowiedź powinna być w formacie:
```json
{
    "task": "gps",
    "apikey": "twój-klucz-api",
    "answer": {
        "imie": {
            "lat": 12.345,
            "lon": 65.431
        },
        "kolejne-imie": {
            "lat": 19.433,
            "lon": 12.123
        }
    }
}
```

## Uwagi
- Nie należy pytać o lokalizację Barbary
- Wszystkie osoby oprócz Barbary powinny mieć zwrócone współrzędne
- Współrzędne powinny być w formacie liczbowym (float) 