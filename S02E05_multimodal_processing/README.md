# Zadanie 0205 - Analiza artykułu profesora Maja

## Opis
Skrypt do analizy artykułu profesora Maja, który przetwarza tekst, obrazy i dźwięki, a następnie generuje odpowiedzi na pytania centrali.

## Wymagania
- Python 3.8+
- Zainstalowane zależności z pliku `requirements.txt`

## Instalacja
1. Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
```

2. Utwórz plik `.env` i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Użycie
1. Uruchom skrypt przetwarzający artykuł:
```bash
python process_article.py
```

2. Uruchom skrypt generujący odpowiedzi:
```bash
python generate_answers.py
```

## Struktura projektu
- `data/` - folder na przetworzone dane
- `cache/` - folder na pliki tymczasowe
- `process_article.py` - skrypt do przetwarzania artykułu
- `generate_answers.py` - skrypt do generowania odpowiedzi
- `requirements.txt` - lista zależności
- `README.md` - dokumentacja

## Format odpowiedzi
Odpowiedzi są generowane w formacie JSON:
```json
{
    "task": "arxiv",
    "apikey": "YOUR_API_KEY",
    "answer": {
        "01": "krótka odpowiedź w 1 zdaniu",
        "02": "krótka odpowiedź w 1 zdaniu",
        "03": "krótka odpowiedź w 1 zdaniu",
        ...
    }
}
```
