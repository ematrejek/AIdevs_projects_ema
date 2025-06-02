# Zadanie photos - Analiza i poprawa zdjęć

Program analizuje i poprawia zdjęcia, aby stworzyć szczegółowy rysopis Barbary. Wykorzystuje model GPT-4o do analizy zdjęć i komunikuje się z centralą w celu poprawy jakości zdjęć.

## Funkcjonalności

1. **Pobieranie i przechowywanie zdjęć**
   - Automatyczne pobieranie zdjęć z centrali
   - Lokalne przechowywanie w katalogu `images`
   - Unikanie ponownego pobierania istniejących zdjęć

2. **Analiza zdjęć**
   - Wykorzystanie modelu GPT-4 Vision do szczegółowej analizy
   - Skupienie na kluczowych cechach:
     - Kolor włosów
     - Znaki szczególne (pieprzyki, blizny, tatuaże)
     - Charakterystyczne cechy wyglądu
     - Ubranie i dodatki
     - Sylwetka i postura

3. **Inteligentne poprawianie zdjęć**
   - Automatyczne wykrywanie problemów na podstawie opisu
   - Wykonywanie operacji w odpowiedniej kolejności:
     1. REPAIR - dla zniekształconych zdjęć
     2. BRIGHTEN - dla zbyt ciemnych zdjęć
     3. DARKEN - dla zbyt jasnych zdjęć
   - Sprawdzanie efektów każdej operacji
   - Wykonywanie kolejnych operacji jeśli są potrzebne

4. **Komunikacja z centralą**
   - Wysyłanie komend do poprawy zdjęć
   - Analiza odpowiedzi centrali
   - Reagowanie na wskazówki dotyczące jakości zdjęć
   - Unikanie niepotrzebnych operacji

5. **Generowanie rysopisu**
   - Zbieranie opisów ze wszystkich wersji zdjęć
   - Tworzenie szczegółowego rysopisu
   - Uwzględnianie wskazówek z centrali
   - Automatyczne ponowne próby z bardziej szczegółowym opisem

## Wymagania

- Python 3.x
- Biblioteki:
  - openai
  - requests
  - python-dotenv
- Klucz API OpenAI
- Klucz API centrali

## Konfiguracja

1. Utwórz plik `.env` z następującymi zmiennymi:
   ```
   OPENAI_API_KEY=twój_klucz_openai
   CENTRALA_URL=url_centrali
   CENTRALA_API_KEY=twój_klucz_centrali
   ```

2. Upewnij się, że masz dostęp do modelu GPT-4 Vision

## Użycie

```bash
python photos.py
```

Program automatycznie:
1. Rozpocznie zadanie w centrali
2. Pobierze dostępne zdjęcia
3. Przeanalizuje i poprawi każde zdjęcie
4. Wygeneruje końcowy rysopis
5. Wyśle rysopis do centrali

## Logika działania

1. **Analiza oryginalnego zdjęcia**
   - Pobranie i zapisanie zdjęcia
   - Analiza przez GPT-4 Vision
   - Wykrycie potrzebnych operacji

2. **Poprawa zdjęcia**
   - Wykonanie wykrytych operacji
   - Analiza poprawionej wersji
   - Wykonanie kolejnych operacji jeśli potrzebne

3. **Generowanie rysopisu**
   - Zbieranie opisów ze wszystkich wersji
   - Tworzenie końcowego rysopisu
   - Uwzględnianie wskazówek z centrali

## Obsługa błędów

- Automatyczne wykrywanie nieudanych operacji
- Reagowanie na komunikaty z centrali
- Unikanie niepotrzebnych operacji
- Ponowne próby z bardziej szczegółowym opisem

## Optymalizacje

1. **Lokalne przechowywanie**
   - Unikanie ponownego pobierania zdjęć
   - Szybszy dostęp do wcześniej pobranych wersji

2. **Inteligentne wykrywanie operacji**
   - Priorytetyzacja operacji (REPAIR > BRIGHTEN/DARKEN)
   - Unikanie niepotrzebnych operacji
   - Sprawdzanie efektów każdej operacji

3. **Efektywne wykorzystanie API**
   - Jedna próba analizy dla każdej wersji
   - Unikanie powtarzania operacji
   - Optymalne wykorzystanie wskazówek z centrali 