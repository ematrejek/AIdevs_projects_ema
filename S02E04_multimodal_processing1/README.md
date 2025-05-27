# Analizator Raportów Fabrycznych

Ten skrypt służy do analizy różnych typów raportów z fabryki, w tym plików tekstowych, obrazów i plików audio. Skrypt klasyfikuje raporty do odpowiednich kategorii i wysyła wyniki do serwera.

## Wymagania

- Python 3.8 lub nowszy
- Klucz API OpenAI (OPENAI_API_KEY)

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj wymagane zależności:
```bash
pip install -r requirements.txt
```
3. Utwórz plik `.env` w głównym katalogu projektu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Użycie

Uruchom skrypt za pomocą komendy:
```bash
python analyze_factory_reports.py
```

## Funkcjonalności

- Analiza plików tekstowych (.txt)
- Analiza obrazów (.png, .jpg, .jpeg)
- Analiza plików audio (.mp3, .wav)
- Automatyczna klasyfikacja do kategorii:
  - people: informacje o schwytanych ludziach lub śladach ich obecności
  - hardware: usterki sprzętowe
  - none: pozostałe przypadki

## Obsługa błędów

W przypadku problemów z wysłaniem raportu, wyniki zostaną zapisane lokalnie w pliku `report.json`.

## Logi

Skrypt generuje szczegółowe logi, które pomagają w debugowaniu i monitorowaniu procesu analizy. 