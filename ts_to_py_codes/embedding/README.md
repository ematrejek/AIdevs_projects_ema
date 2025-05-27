# Projekt Embedding

Ten projekt demonstruje wykorzystanie wektorowych baz danych do wyszukiwania semantycznego. Implementacja wykorzystuje OpenAI do generowania embeddingów tekstowych oraz Qdrant jako bazę danych wektorową.

## Funkcjonalności

- Generowanie embeddingów tekstowych przy użyciu modelu GPT-4
- Przechowywanie wektorów w bazie danych Qdrant
- Wyszukiwanie semantyczne w bazie danych
- Przetwarzanie i dzielenie tekstu na dokumenty

## Struktura projektu

- `app.py` - główny plik aplikacji zawierający przykładowe użycie
- `OpenAIService.py` - serwis do komunikacji z API OpenAI
- `TextService.py` - serwis do przetwarzania tekstu
- `VectorService.py` - serwis do obsługi bazy danych wektorowej

## Wymagania

- Python 3.7+
- OpenAI API key
- Qdrant (lokalnie lub w chmurze)

## Użycie

1. Upewnij się, że masz skonfigurowane wszystkie wymagane zmienne środowiskowe (np. klucz API OpenAI)
2. Zainstaluj wymagane zależności
3. Uruchom aplikację:

```bash
python app.py
```

## Przykład

Aplikacja zawiera przykładowy zestaw danych firm technologicznych i wykonuje wyszukiwanie semantyczne dla następujących zapytań:
- Car company
- Macbooks
- Facebook
- Newsletter

Wyniki wyszukiwania są wyświetlane wraz z wynikami podobieństwa (score). 