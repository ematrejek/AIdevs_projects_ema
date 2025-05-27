# System Cenzury Danych Agentów

Ten projekt implementuje system do automatycznej cenzury danych osobowych agentów. System pobiera dane z API, ocenzurowuje wrażliwe informacje i wysyła je z powrotem do serwera.

## Funkcjonalności

- Pobieranie danych z API co 60 sekund
- Cenzurowanie następujących danych:
  - Imię i nazwisko
  - Wiek
  - Miasto
  - Ulica i numer domu
- Automatyczne wysyłanie ocenzurowanych danych do API

## Wymagania

- Python 3.6+
- Biblioteki wymienione w pliku `requirements.txt`

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj wymagane zależności:
```bash
pip install -r requirements.txt
```

## Konfiguracja

Przed uruchomieniem programu upewnij się, że masz poprawny klucz API. Klucz API jest zdefiniowany w pliku `cenzura.py` jako zmienna `API_KEY`.

## Użycie

Aby uruchomić program, wykonaj:

```bash
python cenzura.py
```

Program będzie działał w nieskończoność, pobierając i przetwarzając dane co 60 sekund.

## Format danych

Program oczekuje danych w formacie tekstowym, np.:
```
Osoba podejrzana to Jan Nowak. Adres: Wrocław, ul. Szeroka 18. Wiek: 32 lata.
```

Po cenzurze dane będą wyglądać tak:
```
Osoba podejrzana to CENZURA. Adres: CENZURA, ul. CENZURA. Wiek: CENZURA lata.
```

## Obsługa błędów

Program automatycznie obsługuje błędy i ponawia próby w przypadku niepowodzenia. W przypadku błędu:
1. Wyświetli komunikat o błędzie
2. Poczeka 5 sekund
3. Spróbuje ponownie wykonać operację 