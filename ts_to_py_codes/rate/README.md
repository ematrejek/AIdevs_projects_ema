# SERP Relevance Evaluator

System do oceny trafności wyników wyszukiwania (SERP) w kontekście web scrapingu.

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Utwórz plik `.env` w głównym katalogu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Użycie

```python
from rate import evaluate_snippet

context = """Resource: https://example.com
Title: Example Page
Snippet: This is an example snippet that we want to evaluate."""
query = "What is this page about?"

result = evaluate_snippet(context, query)
print(result)
```

## Testy

Aby uruchomić testy:
```bash
python -m unittest test_rate.py
```

## Struktura projektu

- `rate.py` - główny moduł z funkcją oceny trafności
- `test_rate.py` - testy jednostkowe
- `requirements.txt` - zależności projektu
- `README.md` - dokumentacja 