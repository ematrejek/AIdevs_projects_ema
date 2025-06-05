# API do sterowania dronem

## Opis
API do sterowania dronem po mapie 4x4. Dron zawsze startuje z lewego górnego rogu (0,0) i może być sterowany za pomocą instrukcji w języku naturalnym.

## Mapa
```
start    trawa    drzewo   dom
trawa    wiatrak  trawa    trawa
trawa    trawa    skały    dwa drzewa
góry     góry     samochód jaskinia
```

## Instalacja
1. Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
```

2. Uruchom serwer:
```bash
python server.py
```

## Użycie API
Endpoint: `POST /dron`

Przykładowe żądanie:
```json
{
    "instruction": "dwa kroki w prawo, potem na dół"
}
```

Przykładowa odpowiedź:
```json
{
    "description": "trawa"
}
```

## Obsługiwane instrukcje
- Ruchy względne:
  - "jeden krok w prawo"
  - "dwa pola w lewo"
  - "trzy kroki w górę"
  - "cztery kratki w dół"

- Ruchy maksymalne:
  - "na maksa w prawo"
  - "do końca w lewo"
  - "ile wlezie w dół"
  - "na samą górę"

- Reset pozycji:
  - "zaczynamy od nowa"
  - "od nowa"

## System logowania
System logowania został zaimplementowany w celu ułatwienia debugowania. Logi są zapisywane w katalogu `logs` w plikach o nazwach w formacie `dron_YYYYMMDD_HHMMSS.log`.

Logi zawierają:
- Szczegółowe informacje o przetwarzaniu każdej instrukcji
- Pozycję drona przed i po każdym ruchu
- Wykryte liczby i kierunki
- Ostrzeżenia o timeoutach
- Błędy i wyjątki

Przykładowy log:
```
2024-03-14 15:30:45,123 - INFO - Rozpoczęto logowanie do pliku: logs/dron_20240314_153045.log
2024-03-14 15:30:46,234 - INFO - Otrzymano nowe żądanie z instrukcją: 'dwa kroki w prawo'
2024-03-14 15:30:46,235 - INFO - Wykryto liczbę słowną: 2
2024-03-14 15:30:46,236 - INFO - Wykryto kierunek: w prawo (dx=1, dy=0)
2024-03-14 15:30:46,237 - INFO - Wykonano ruch: (0, 0) -> (2, 0)
```

## Obsługa błędów
- Puste instrukcje zwracają opis punktu startowego
- Nieprawidłowe instrukcje są ignorowane
- Błędy przetwarzania zwracają status 500
- Timeout dla przetwarzania instrukcji: 100ms

## Bezpieczeństwo
- Walidacja długości instrukcji (1-1000 znaków)
- Ograniczenie pozycji do granic mapy (0-3)
- Timeout dla przetwarzania instrukcji 