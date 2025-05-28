# query_db.py

## Opis

Skrypt `query_db.py` służy do komunikacji z bazą danych poprzez API, odkrywania jej struktury oraz wykonywania zapytań SQL. W szczególności pozwala znaleźć aktywne centra danych, których menedżerowie są nieaktywni.

## Wymagania

- Python 3.x
- Biblioteka `requests`

Instalacja wymaganych bibliotek:
```bash
pip install requests
```

## Użycie

1. Uruchom skrypt:
   ```bash
   python query_db.py
   ```
2. Skrypt:
   - Wyświetli dostępne tabele w bazie danych
   - Pokaże strukturę kluczowych tabel (`users`, `datacenters`, `connections`)
   - Wykona zapytanie SQL, które znajdzie aktywne centra danych z nieaktywnymi menedżerami
   - Wyświetli wynik zapytania oraz gotową odpowiedź do przesłania do centrali

## Przykładowy wynik

```
Dostępne tabele: ...
Struktura tabeli users: ...
Struktura tabeli datacenters: ...
Struktura tabeli connections: ...
Wynik zapytania: ...
Odpowiedź do centrali: ...
```

## Edycja zapytania

Aby zmienić zapytanie SQL, edytuj zmienną `query` w pliku `query_db.py`.
