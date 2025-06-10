# Chat API z OpenAI

Prosta aplikacja FastAPI do prowadzenia konwersacji z modelem OpenAI GPT-4, z funkcją zapamiętywania historii konwersacji i automatycznym generowaniem podsumowań.

## Funkcje

- Prowadzenie konwersacji z modelem GPT-4
- Automatyczne zapamiętywanie historii konwersacji
- Dynamiczne generowanie podsumowań konwersacji po każdej wymianie
- Endpoint demo do testowania z predefiniowanymi wiadomościami
- Asystent skonfigurowany do zwięzłych odpowiedzi

## Wymagania

- Python 3.8+
- Konto OpenAI z kluczem API

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone <url-repozytorium>
cd thread
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Utwórz plik `.env` w głównym katalogu projektu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Uruchomienie

Uruchom serwer:
```bash
python app.py
```

Serwer będzie dostępny pod adresem `http://localhost:3000`

## API Endpoints

### POST /api/chat

Wysyłanie wiadomości do asystenta. Każda wymiana automatycznie aktualizuje podsumowanie konwersacji.

Przykładowe zapytanie:
```bash
curl -X POST http://localhost:3000/api/chat \
-H "Content-Type: application/json" \
-d '{
    "message": {
        "role": "user",
        "content": "Cześć, jak się masz?"
    }
}'
```

### POST /api/demo

Uruchamia przykładową konwersację z trzema wstępnie zdefiniowanymi wiadomościami:
1. "Hi! I'm Adam"
2. "How are you?"
3. "Do you know my name?"

Każda wymiana jest automatycznie podsumowywana i dodawana do historii konwersacji.

Przykładowe zapytanie:
```bash
curl -X POST http://localhost:3000/api/demo
```

## Struktura projektu

- `app.py` - główny plik aplikacji
- `requirements.txt` - lista zależności
- `.env` - plik konfiguracyjny z kluczem API

## Klasy

### Conversation
Zarządza historią konwersacji i podsumowaniami:
- `messages` - lista wszystkich wiadomości w formacie `{"role": str, "content": str}`
- `summary` - aktualne podsumowanie konwersacji
- `add_message(role, content)` - dodaje nową wiadomość do historii
- `update_summary(summary)` - aktualizuje podsumowanie konwersacji

### LLMHandler
Obsługuje komunikację z API OpenAI:
- `get_completion(messages)` - wysyła zapytanie do API i zwraca odpowiedź
- `create_system_prompt()` - tworzy prompt systemowy z uwzględnieniem podsumowania konwersacji
- `generate_summarization(user_message, assistant_response)` - generuje nowe podsumowanie na podstawie bieżącej wymiany i poprzedniego podsumowania

## Uwagi

- Aplikacja przechowuje historię konwersacji w pamięci, więc jest resetowana po restarcie serwera
- Domyślnie używany jest model GPT-4
- Asystent jest skonfigurowany do odpowiadania zwięźle
- Podsumowania konwersacji są generowane po każdej wymianie, co pozwala na lepszy kontekst dla kolejnych odpowiedzi
- Demo endpoint pokazuje przykładową konwersację z predefiniowanymi wiadomościami 