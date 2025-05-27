# Generator Podsumowań Artykułów

## Opis
Ten projekt to zaawansowany generator podsumowań artykułów, wykorzystujący modele językowego AI do tworzenia szczegółowych i precyzyjnych streszczeń. System analizuje tekst wejściowy, wyciąga kluczowe informacje i generuje kompleksowe podsumowanie, zachowując oryginalny kontekst i znaczenie.

## Funkcjonalności
- Ekstrakcja kluczowych informacji z tekstu
- Identyfikacja głównych tematów i podtematów
- Analiza kontekstu i tła
- Generowanie szczegółowych podsumowań
- Automatyczna krytyka i weryfikacja wygenerowanych podsumowań
- Zachowanie oryginalnego formatowania i struktury

## Wymagania
- Python 3.7+
- Biblioteka OpenAI
- Zmienna środowiskowa OPENAI_API_KEY

## Instalacja
1. Sklonuj repozytorium
2. Zainstaluj wymagane zależności:
```bash
pip install openai python-dotenv
```
3. Utwórz plik `.env` i dodaj swój klucz API OpenAI:
```
OPENAI_API_KEY=twój_klucz_api
```

## Użycie
1. Umieść tekst artykułu w pliku `article.md` w katalogu głównym projektu
2. Uruchom skrypt:
```bash
python summary_app.py
```
3. Wygenerowane podsumowania zostaną zapisane w katalogu `summary_output`

## Struktura wyjściowa
W katalogu `summary_output` znajdziesz następujące pliki:
1. `1_topics.md` - Główne tematy artykułu
2. `2_entities.md` - Wymienione osoby, miejsca i rzeczy
3. `3_keywords.md` - Kluczowe terminy i frazy
4. `4_links.md` - Lista linków i obrazów
5. `5_resources.md` - Wymienione narzędzia i zasoby
6. `6_takeaways.md` - Główne wnioski
7. `7_context.md` - Informacje kontekstowe
8. `8_draft_summary.md` - Wersja robocza podsumowania
9. `9_summary_critique.md` - Analiza krytyczna podsumowania
10. `10_final_summary.md` - Ostateczna wersja podsumowania

## Uwagi
- System wymaga dostępu do API OpenAI
- Generowanie podsumowań może zająć kilka minut, w zależności od długości tekstu
- Wszystkie podsumowania są generowane w języku polskim
- System zachowuje oryginalne formatowanie markdown

## Licencja
MIT 