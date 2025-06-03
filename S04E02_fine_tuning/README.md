# Weryfikacja danych laboratoryjnych z wykorzystaniem fine-tuningu

## Opis zadania
Zadanie polegało na weryfikacji wyników badań laboratoryjnych, gdzie część wyników została potencjalnie sfałszowana. Mając dostęp do zbioru poprawnych i niepoprawnych wyników, należało wytrenować model do wykrywania fałszywych odczytów.

## Struktura projektu
- `correct.txt` - zawiera przykłady poprawnych wyników badań
- `incorrect.txt` - zawiera przykłady niepoprawnych wyników badań
- `verify.txt` - zawiera wyniki do weryfikacji
- `generate_finetune_jsonl.py` - skrypt do przygotowania danych do fine-tuningu
- `verify_data.py` - skrypt do weryfikacji wyników przy użyciu wytrenowanego modelu
- `finetune_data.jsonl` - wygenerowany plik z danymi do fine-tuningu
- `.env` - plik z konfiguracją i kluczami API

## Konfiguracja
Utwórz plik `.env` w głównym katalogu projektu z następującymi zmiennymi:
```env
OPENAI_API_KEY=twój_klucz_api_openai
CENTRAL_API_KEY=twój_klucz_api_centrali
CENTRAL_API_URL=https://c3ntrala.ag3nts.org/report
FINE_TUNED_MODEL=nazwa_twojego_wytrenowanego_modelu
```

## Proces fine-tuningu

### 1. Przygotowanie danych
Dane zostały przygotowane w formacie JSONL zgodnym z wymaganiami OpenAI dla fine-tuningu. Każda linia zawiera:
- System prompt: "validate data"
- User prompt: dane z jednej linii pliku
- Assistant response: "1" dla poprawnych danych, "0" dla niepoprawnych

Skrypt `generate_finetune_jsonl.py` automatycznie przetwarza pliki `correct.txt` i `incorrect.txt` do wymaganego formatu.

### 2. Trenowanie modelu
Fine-tuning został wykonany na platformie OpenAI:
- Model bazowy: gpt-4o-mini-2024-07-18
- Metoda: Supervised
- Dane treningowe: wygenerowany plik JSONL
- Dane walidacyjne: automatycznie wybrane z danych treningowych

### 3. Weryfikacja wyników
Po wytrenowaniu modelu, skrypt `verify_data.py`:
1. Wczytuje dane z pliku `verify.txt`
2. Dla każdej linii wysyła zapytanie do wytrenowanego modelu
3. Zbiera identyfikatory (pierwsze dwie cyfry) z linii oznaczonych jako poprawne
4. Wysyła raport do centrali w formacie:
```json
{
    "task": "research",
    "apikey": "TWÓJ_KLUCZ_API",
    "answer": ["01", "02", "03", ...]
}
```

## Uruchomienie

1. Instalacja zależności:
```bash
pip install -r requirements.txt
```

2. Przygotowanie danych do fine-tuningu:
```bash
python generate_finetune_jsonl.py
```

3. Weryfikacja wyników:
```bash
python verify_data.py
```

## Wymagania
- Python 3.x
- Biblioteki: openai, python-dotenv, requests
- Plik `.env` z odpowiednimi zmiennymi środowiskowymi 