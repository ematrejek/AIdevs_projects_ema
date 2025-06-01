# Znajdowanie ścieżki między osobami w grafie

Ten projekt rozwiązuje zadanie polegające na znalezieniu najkrótszej ścieżki między dwiema osobami w grafie społecznościowym. Wykorzystuje bazę danych Neo4j do przechowywania i analizy relacji między osobami.

## Wymagania

- Python 3.8+
- Neo4j Database
- Biblioteki Python (zainstaluj je używając `pip install -r requirements.txt`):
  - python-dotenv
  - requests
  - neo4j

## Konfiguracja

1. Utwórz plik `.env` w głównym katalogu projektu z następującymi zmiennymi:
```env
API_DB_URL=https://c3ntrala.ag3nts.org/apidb
REPORT_URL=https://c3ntrala.ag3nts.org/report
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=twoje_haslo
AIDEVS_API_KEY=twój_klucz
```

2. Upewnij się, że masz uruchomioną lokalną instancję Neo4j Database.

## Struktura projektu

- `main.py` - główny plik z implementacją
- `requirements.txt` - lista wymaganych bibliotek
- `.env` - plik z konfiguracją (nie jest w repozytorium)

## Jak to działa

1. Program pobiera dane o użytkownikach i ich połączeniach z API
2. Tworzy węzły w bazie Neo4j dla każdej osoby
3. Tworzy relacje KNOWS między osobami, które się znają
4. Znajduje najkrótszą ścieżkę między dwiema wskazanymi osobami (Rafał -> Barbara)
5. Wysyła wynik do API

## Uruchomienie

```bash
python main.py
```

## Obsługa błędów

Program zawiera podstawową obsługę błędów dla:
- Problemów z połączeniem do Neo4j
- Błędów podczas pobierania danych z API
- Braku danych użytkowników
- Problemów z wysyłaniem odpowiedzi

## Bezpieczeństwo

- Wszystkie dane wrażliwe (hasła, klucze API) są przechowywane w pliku `.env`
- Połączenia HTTPS są używane do komunikacji z API
- Weryfikacja SSL jest wyłączona dla celów deweloperskich 