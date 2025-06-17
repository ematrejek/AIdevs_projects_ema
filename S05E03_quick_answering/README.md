# S05E03 - Szybkie odpowiadanie

## Opis zadania
Zadanie polega na szybkim odpowiadaniu na pytania z wykorzystaniem API OpenAI. Program musi pobrać zadania z serwera, przetworzyć je przy użyciu modelu GPT-3.5 Turbo i zwrócić odpowiedzi w określonym czasie.

## Wymagania
- Python 3.7+
- Biblioteki wymienione w `requirements.txt`
- Klucz API OpenAI
- Klucz API do serwera zadań

## Konfiguracja
1. Utwórz plik `.env` w głównym katalogu projektu z następującymi zmiennymi:
```
API_KEY=twój_klucz_api
BASE_URL=url_serwera
PASSWORD=hasło_do_serwera
OPENAI_API_KEY=twój_klucz_openai
```

## Struktura projektu
```
S05E03_quick_answering/
├── solution.py      # Główny plik z rozwiązaniem
├── requirements.txt # Zależności projektu
├── .env            # Plik z konfiguracją (do utworzenia)
├── logs/           # Katalog z logami
└── results/        # Katalog z wynikami
```

## Uruchomienie
1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Uruchom program:
```bash
python solution.py
```

## Funkcjonalności
- Asynchroniczne pobieranie i przetwarzanie zadań
- Cachowanie danych źródłowych
- Automatyczne logowanie do pliku
- Obsługa błędów i ponowne próby
- Optymalizacja czasu odpowiedzi

## Optymalizacje
- Użycie asynchronicznych zapytań HTTP
- Implementacja cache'u dla danych źródłowych
- Minimalizacja tokenów w zapytaniach do GPT
- Efektywne zarządzanie zasobami

## Logi
Program generuje logi w katalogu `logs/` z informacjami o:
- Czasie wykonania
- Błędach
- Statusie operacji

## Autor
Rozwiązanie zostało przygotowane jako część zadania S05E03. 