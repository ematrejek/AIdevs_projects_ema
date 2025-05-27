# Analiza Głosu - Transkrypcja Audio

Ten projekt służy do transkrypcji plików audio w formacie .m4a na tekst przy użyciu modelu Whisper od OpenAI.

## Wymagania

- Python 3.7+
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

## Użycie

1. Umieść pliki audio w formacie .m4a w głównym katalogu projektu
2. Uruchom skrypt transkrypcji:
```bash
python transcribe.py
```
3. Transkrypcje zostaną zapisane w pliku `transcripts.json`

## Struktura projektu

- `transcribe.py` - główny skrypt do transkrypcji audio
- `send_answer.py` - skrypt do wysyłania odpowiedzi na serwer
- `transcripts.json` - plik zawierający transkrypcje
- `requirements.txt` - lista wymaganych zależności
- `.env` - plik konfiguracyjny z kluczem API (nie jest commitowany do repozytorium)

## Uwagi

- Skrypt automatycznie wykrywa pliki .m4a w katalogu
- Transkrypcje są zapisywane w formacie JSON z kodowaniem UTF-8
- Domyślnie używany jest model "whisper-1" z językiem polskim 