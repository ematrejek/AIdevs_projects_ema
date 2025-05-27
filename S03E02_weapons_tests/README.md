# Indeksowanie i Wyszukiwanie Raportów z Testów Broni

Ten projekt implementuje system indeksowania i wyszukiwania semantycznego dla raportów z testów broni, wykorzystując bazę wektorową Qdrant oraz model embeddingów OpenAI.

## Wymagania

- Python 3.8+
- Docker (opcjonalnie, jeśli chcemy używać Qdrant w kontenerze)
- Klucz API OpenAI

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj wymagane zależności:
```bash
pip install -r requirements.txt
```
3. Utwórz plik `.env` w głównym katalogu projektu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Struktura Projektu

```
weapons_tests/
├── do-not-share/          # Katalog z raportami testów - niedostępny ze względu na ownership danych
├── index_reports.py       # Główny skrypt indeksujący i wyszukujący
├── requirements.txt       # Zależności projektu
└── README.md             # Ten plik
```

## Użycie

1. Upewnij się, że masz skonfigurowany plik `.env` z kluczem API OpenAI
2. Uruchom skrypt:
```bash
python index_reports.py
```

Skrypt:
- Utworzy kolekcję w bazie Qdrant (w trybie in-memory)
- Przetworzy wszystkie raporty z katalogu `do-not-share`
- Wygeneruje embeddingi dla każdego raportu
- Zapisze raporty w bazie Qdrant wraz z metadanymi
- Wyszuka informacje o kradzieży prototypu broni
- Wyświetli znalezioną datę w formacie YYYY-MM-DD

## Technologie

- **Qdrant**: Baza wektorowa używana do przechowywania i wyszukiwania embeddingów
- **OpenAI API**: Model text-embedding-3-large do generowania embeddingów
- **Python**: Język programowania
- **requests**: Biblioteka do komunikacji z API
- **python-dotenv**: Zarządzanie zmiennymi środowiskowymi

## Uwagi

- Skrypt używa Qdrant w trybie in-memory, co oznacza, że dane są przechowywane tylko w pamięci i są tracone po zakończeniu działania skryptu
- Dla większych zbiorów danych zalecane jest użycie Qdrant w kontenerze Docker
- Model embeddingów text-embedding-3-large generuje wektory o wymiarze 3072
