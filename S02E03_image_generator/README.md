# Generator Obrazów Robotów

Ten skrypt automatycznie pobiera opis robota z API, generuje jego obraz używając DALL-E 3 i wysyła raport do centrali.

## Wymagania

- Python 3.8+
- Klucz API OpenAI (DALL-E 3)
- Klucz API do centrali

## Instalacja

1. Utwórz wirtualne środowisko:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Utwórz plik `.env` w katalogu projektu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api_openai
```

## Użycie

Uruchom skrypt:
```bash
python robot_generator.py
```

Skrypt:
1. Pobierze aktualny opis robota z API
2. Wygeneruje obraz używając DALL-E 3
3. Wyśle raport z URL obrazu do centrali

## Uwagi

- Opis robota zmienia się co 10 minut
- Obraz jest generowany w formacie PNG o wymiarach 1024x1024px
- URL obrazu jest automatycznie wysyłany do centrali 