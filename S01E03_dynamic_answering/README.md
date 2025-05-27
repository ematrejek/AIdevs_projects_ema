# Zadanie JSON - Poprawa pliku kalibracyjnego

## Opis zadania
Zadanie polega na poprawieniu pliku kalibracyjnego dla robota przemysłowego. Plik zawiera błędy w obliczeniach oraz wymaga uzupełnienia odpowiedzi na pytania otwarte.

## Główne cele
1. Pobranie pliku TXT z danymi kalibracyjnymi
2. Poprawienie błędów w obliczeniach
3. Uzupełnienie odpowiedzi na pytania otwarte przy użyciu LLM
4. Wysłanie poprawionego pliku w odpowiednim formacie

## Szczegóły implementacji
- Skrypt pobiera dane z pliku TXT dostępnego pod adresem: `https://c3ntrala.ag3nts.org/data/{API_KEY}/json.txt`
- Poprawia błędy w obliczeniach programistycznie
- Używa LLM do generowania odpowiedzi na pytania otwarte
- Wysyła poprawiony plik w formacie JSON na endpoint: `https://c3ntrala.ag3nts.org/report`

## Format odpowiedzi
```json
{
  "task": "JSON",
  "apikey": "TWÓJ-KLUCZ-API",
  "answer": {
    "apikey": "TWÓJ-KLUCZ-API",
    "description": "This is simple calibration data used for testing purposes. Do not use it in production environment!",
    "copyright": "Copyright (C) 2238 by BanAN Technologies Inc.",
    "test-data": [
      // Poprawione dane testowe
    ]
  }
}
```

## Wymagania
- Python 3.x
- Biblioteki: requests, beautifulsoup4, openai, python-dotenv
- Klucz API do OpenAI
- Klucz API do systemu centrali

## Instalacja
1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Utwórz plik `.env` z kluczami API:
```
OPENAI_API_KEY=twój_klucz_openai
CENTRAL_API_KEY=twój_klucz_centrali
```

## Uruchomienie
```bash
python login.py
``` 