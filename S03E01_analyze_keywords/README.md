# Analizator Raportów Fabryki

## Opis
Skrypt do analizy raportów z fabryki, który generuje słowa kluczowe na podstawie treści raportów i powiązanych faktów. Skrypt wykorzystuje OpenAI API do analizy tekstu i generowania precyzyjnych słów kluczowych w języku polskim.

## Wymagania
- Python 3.6+
- Klucz API OpenAI
- Wymagane pakiety (z pliku requirements.txt):
  - openai==1.3.0
  - python-dotenv==1.0.0
  - requests==2.31.0

## Instalacja
1. Sklonuj repozytorium
2. Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
```
3. Utwórz plik `.env` w głównym katalogu projektu i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Struktura Projektu
```
pliki_z_fabryki/
├── analyze_keywords.py    # Główny skrypt analizujący
├── requirements.txt       # Zależności projektu
├── .env                  # Plik z kluczem API (do utworzenia)
├── cache/                # Katalog na pliki cache
│   └── keywords/         # Cache wygenerowanych słów kluczowych
├── fakty/                # Katalog z plikami faktów - niedostępny ze względu na ownership danych
└── README.md            # Ten plik
```

## Funkcjonalności
- Analiza raportów z fabryki w formacie TXT
- Ekstrakcja kluczowych informacji z faktów
- Generowanie słów kluczowych w języku polskim
- Automatyczne wykrywanie powiązań między raportami a faktami
- System cache'owania wyników
- Obsługa błędów i ponownych prób przy problemach z API
- Generowanie raportu końcowego w formacie JSON

## Użycie
1. Upewnij się, że masz skonfigurowany plik `.env` z kluczem API
2. Umieść pliki raportów w głównym katalogu projektu
3. Umieść pliki faktów w katalogu `fakty/`
4. Uruchom skrypt:
```bash
python analyze_keywords.py
```

## Format Wyjściowy
Skrypt generuje plik `final_report.json` zawierający słowa kluczowe dla każdego raportu w formacie:
```json
{
    "task": "dokumenty",
    "apikey": "twój_klucz_api",
    "answer": {
        "nazwa_pliku_raportu.txt": "słowo1,słowo2,słowo3",
        ...
    }
}
```

## Obsługa Błędów
- Automatyczne ponowne próby przy błędach API
- Logowanie błędów do konsoli
- Zapisywanie postępu w cache
- Walidacja liczby przeanalizowanych raportów

## Cache
Skrypt wykorzystuje system cache'owania do:
- Przechowywania mapy osób i ich atrybutów
- Zapisywania wygenerowanych słów kluczowych
- Przyspieszenia ponownych analiz

## Uwagi
- Skrypt wymaga połączenia z internetem do komunikacji z API OpenAI
- Zalecane jest używanie modelu GPT-4 dla najlepszych wyników
- Domyślny czas oczekiwania między raportami to 15 sekund 