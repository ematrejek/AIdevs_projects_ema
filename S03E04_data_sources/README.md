# Poszukiwania Barbary Zawadzkiej

## Opis projektu
Ten projekt służy do poszukiwania Barbary Zawadzkiej poprzez analizę danych z dwóch systemów:
1. Wyszukiwarka członków ruchu oporu (`/people`) - zwraca listę miejsc, w których widziano daną osobę
2. Wyszukiwarka miejsc (`/places`) - zwraca listę osób widzianych w danym miejscu

## Struktura projektu
```
S03E04_data_sources/
├── main.py           # Główny skrypt
├── requirements.txt  # Zależności projektu
├── .env             # Plik z kluczem API
└── results/         # Katalog z wynikami
    ├── people/      # Wyniki dotyczące osób
    ├── places/      # Wyniki dotyczące miejsc
    └── flags/       # Znalezione flagi i znaki specjalne
```

## Wymagania
- Python 3.6+
- Biblioteki z pliku `requirements.txt`

## Instalacja
1. Zainstaluj wymagane biblioteki:
```bash
pip install -r requirements.txt
```

2. Utwórz plik `.env` z kluczem API:
```
API_KEY=twój_klucz_api
```

## Uruchomienie
```bash
python main.py
```

## Funkcjonalności
- Pobieranie i analiza notatki o Barbarze
- Automatyczne wyszukiwanie powiązań między osobami a miejscami
- Zapisywanie wszystkich znalezionych informacji w strukturze katalogów
- Wykrywanie ukrytych flag i znaków specjalnych w odpowiedziach API
- Normalizacja imion (obsługa różnych wersji tego samego imienia)

## Format danych
Skrypt zapisuje wszystkie znalezione informacje w plikach JSON w katalogu `results/`:
- `people/` - informacje o osobach i ich lokalizacjach
- `places/` - informacje o miejscach i osobach w nich widzianych
- `flags/` - znalezione flagi i znaki specjalne

## Przykład użycia
1. Uruchom skrypt
2. Skrypt automatycznie:
   - Pobierze notatkę o Barbarze
   - Przeanalizuje imiona i miasta
   - Rozpocznie iteracyjne wyszukiwanie
   - Zapisze wszystkie znalezione informacje
   - Wyświetli lokalizację Barbary (jeśli zostanie znaleziona)

## Uwagi
- Skrypt ignoruje odpowiedzi zawierające "[**RESTRICTED DATA**]"
- Wszystkie imiona i nazwy miast są normalizowane (usuwane polskie znaki, konwersja na wielkie litery)
- Skrypt zapisuje postęp po każdej iteracji, co pozwala na analizę procesu wyszukiwania 