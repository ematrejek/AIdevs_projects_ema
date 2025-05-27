# System Czatu z Pamięcią

Aplikacja FastAPI implementująca system czatu z zaawansowanym zarządzaniem pamięcią i integracją z OpenAI.

## Funkcjonalności

- Endpoint czatu (`/api/chat`) z obsługą konwersacji
- System zarządzania pamięcią i uczenia się
- Synchronizacja pamięci (`/api/sync`)
- Integracja z OpenAI
- Obsługa wielu konwersacji z unikalnymi identyfikatorami

## Wymagania

- Python 3.8+
- FastAPI
- Uvicorn
- OpenAI API
- Pydantic

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:
```bash
pip install fastapi uvicorn openai pydantic
```

## Konfiguracja

Upewnij się, że masz skonfigurowany klucz API OpenAI w odpowiednim miejscu w aplikacji.

## Uruchomienie

Aby uruchomić aplikację:

```bash
python app.py
```

Aplikacja będzie dostępna pod adresem `http://localhost:3000`

## Endpointy API

### POST /api/chat
Endpoint do obsługi czatu. Akceptuje:
- Lista wiadomości
- Opcjonalny identyfikator konwersacji

### POST /api/sync
Endpoint do synchronizacji pamięci systemu.

## Struktura Projektu

- `app.py` - Główny plik aplikacji
- `OpenAIService.py` - Serwis do obsługi OpenAI
- `MemoryService.py` - Serwis zarządzający pamięcią
- `AssistantService.py` - Serwis asystenta
- `prompts.py` - Plik z promptami i strukturą pamięci 