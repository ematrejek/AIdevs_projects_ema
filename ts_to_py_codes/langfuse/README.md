# API Chat z Integracją Langfuse

## Opis
Aplikacja FastAPI, która implementuje endpoint chat z integracją Langfuse do monitorowania i śledzenia interakcji z modelem językowym. Aplikacja wykonuje trzy uzupełnienia (completions) w ramach jednego żądania i śledzi je za pomocą Langfuse.

## Wymagania
- Python 3.x
- FastAPI
- Langfuse
- OpenAI API (przez chat_service)

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:
```bash
pip install fastapi uvicorn langfuse openai
```

## Konfiguracja
Upewnij się, że masz skonfigurowane następujące zmienne środowiskowe:
- Klucze API dla Langfuse
- Klucze API dla OpenAI

## Uruchomienie
```bash
python app.py
```
Aplikacja będzie dostępna pod adresem `http://localhost:3000`

## Endpointy

### POST /api/chat
Endpoint do obsługi czatu z modelem językowym.

#### Parametry żądania
```json
{
    "messages": [
        {
            "role": "string",
            "content": "string",
            "name": "string (opcjonalne)"
        }
    ],
    "conversation_id": "string (opcjonalne)"
}
```

#### Odpowiedź
```json
{
    "completion": "string",
    "completion2": "string",
    "completion3": "string",
    "conversation_id": "string"
}
```

## Funkcjonalności
- Automatyczne generowanie ID konwersacji
- Integracja z Langfuse do monitorowania
- Trzy uzupełnienia w ramach jednego żądania
- Obsługa błędów i wyjątków
- Śledzenie całej konwersacji

## Struktura projektu
- `app.py` - główny plik aplikacji
- `chat_service.py` - serwis do obsługi czatu
- `langfuse_service.py` - serwis do integracji z Langfuse 