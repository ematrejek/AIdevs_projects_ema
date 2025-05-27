# Asystent AI z Kontekstem

Aplikacja FastAPI implementująca inteligentnego asystenta AI z możliwością zapamiętywania kontekstu konwersacji i historii.

## Funkcjonalności

- Chat z asystentem AI wykorzystujący model GPT-4
- Zapamiętywanie kontekstu konwersacji
- Historia konwersacji z możliwością wyszukiwania
- System wspomnień i podobnych kontekstów
- Embeddingi tekstu do wyszukiwania semantycznego

## Wymagania

- Python 3.7+
- FastAPI
- OpenAI API
- Uvicorn
- python-dotenv

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```
3. Utwórz plik `.env` i dodaj klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Uruchomienie

```bash
python app.py
```

Aplikacja będzie dostępna pod adresem `http://localhost:3001`

## API Endpoints

### POST /api/chat
- Wysyłanie wiadomości do asystenta
- Wymaga body z formatem:
```json
{
    "messages": [
        {"role": "user", "content": "treść wiadomości"}
    ],
    "conversation_id": "opcjonalny_id_konwersacji"
}
```

### GET /api/history
- Pobieranie listy wszystkich konwersacji
- Zwraca historię z pierwszym i ostatnim komunikatem

### GET /api/history/{conversation_id}
- Pobieranie szczegółów konkretnej konwersacji

## Struktura Projektu

- `app.py` - główny plik aplikacji
- `context/` - katalog przechowujący historię konwersacji
- `.env` - plik konfiguracyjny ze zmiennymi środowiskowymi

## Bezpieczeństwo

- Klucz API OpenAI jest przechowywany w zmiennych środowiskowych
- Implementacja obsługi błędów i wyjątków
- Walidacja danych wejściowych

## Licencja

MIT 