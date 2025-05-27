# Analizator Map z GPT-4o

Ten projekt wykorzystuje model GPT-4o do analizy fragmentów map miejskich. Program identyfikuje nazwy ulic, charakterystyczne obiekty oraz układ urbanistyczny na podstawie dostarczonych obrazów.

## Wymagania

- Python 3.x
- Klucz API OpenAI
- Wymagane biblioteki:
  - PIL (Pillow)
  - requests
  - python-dotenv

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj wymagane biblioteki:
```bash
pip install Pillow requests python-dotenv
```
3. Utwórz plik `.env` w głównym katalogu projektu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Użycie

1. Umieść obrazy map (format .jpg lub .png) w katalogu z programem
2. Uruchom program:
```bash
python analyze_maps.py
```

Program przeanalizuje wszystkie obrazy w katalogu i wyświetli wyniki zawierające:
- Listę widocznych ulic
- Charakterystyczne obiekty
- Opis układu urbanistycznego
- Prawdopodobną nazwę miasta (jeśli możliwa do określenia)

## Struktura projektu

- `analyze_maps.py` - główny plik programu
- `.env` - plik konfiguracyjny z kluczem API
- Katalog z obrazami map do analizy

## Uwagi

- Program wymaga dostępu do modelu GPT-4o w koncie OpenAI
- Jakość analizy zależy od jakości i czytelności dostarczonych obrazów
- Zalecane jest używanie obrazów w formacie JPEG lub PNG 