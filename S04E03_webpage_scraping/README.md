# Scraper do wyszukiwania informacji na stronie SoftoAI

## Opis projektu
Ten projekt implementuje inteligentnego scrapera, który przeszukuje stronę internetową w poszukiwaniu odpowiedzi na konkretne pytania. Scraper wykorzystuje model językowy (LLM) do analizy treści i podejmowania decyzji o nawigacji po stronie.

## Wymagania
- Python 3.8+
- Biblioteki wymienione w `requirements.txt`

## Instalacja
1. Sklonuj repozytorium
2. Utwórz wirtualne środowisko:
```bash
python -m venv venv
source venv/bin/activate  # dla Linux/Mac
venv\Scripts\activate     # dla Windows
```
3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie
```bash
python scraper.py
```

## Jak to działa
1. Scraper pobiera pytania z API
2. Dla każdego pytania:
   - Rozpoczyna przeszukiwanie od strony głównej
   - Analizuje treść strony używając LLM
   - Jeśli nie znajdzie odpowiedzi, wybiera najbardziej obiecujący link do sprawdzenia
   - Kontynuuje proces do znalezienia odpowiedzi lub osiągnięcia limitu głębokości
3. Zbiera wszystkie odpowiedzi i wysyła raport

## Funkcje
- Inteligentna nawigacja po stronie
- Konwersja HTML do Markdown dla lepszej analizy
- Zapobieganie pętlom poprzez śledzenie odwiedzonych URL-i
- Szczegółowe logowanie procesu wyszukiwania
- Obsługa różnych typów odpowiedzi (tekst, URL-e)

## Struktura projektu
```
S04E03_article_scraping/
├── scraper.py          # Główny kod scrapera
├── requirements.txt    # Zależności projektu
├── .env               # Plik konfiguracyjny
└── README.md          # Ten plik
```

## Uwagi
- Scraper używa modelu GPT-4 do analizy treści
- Maksymalna głębokość przeszukiwania to 3 poziomy
- Odpowiedzi są zwracane w zwięzłej formie
- URL-e są automatycznie formatowane (usuwane cudzysłowy) 