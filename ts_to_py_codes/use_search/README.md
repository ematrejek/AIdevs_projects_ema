# use_search – Testowanie klasyfikatora zapytań

Ten projekt służy do testowania klasyfikatora, który określa, czy dane zapytanie wymaga wyszukania informacji w internecie (np. przez LLM lub API OpenAI).

## Pliki
- `use_search.py` – funkcja pomocnicza do generowania promptów dla modelu
- `use_search_tests.py` – testy, które wypisują tabelę z wynikami w stylu screena

## Jak uruchomić testy?
1. Upewnij się, że masz zainstalowanego Pythona 3.x
2. Uruchom testy poleceniem:
   ```bash
   python use_search_tests.py
   ```

Wynik działania to czytelna tabela z kolumnami:
- query – treść zapytania
- expected – oczekiwany wynik (0 lub 1)
- actual – wynik zwrócony przez funkcję (tu: mockowana logika)
- result – [PASS] jeśli zgodne, [FAIL] jeśli niezgodne

Przykład:
```
query                                                       | expected | actual | result
-----------------------------------------------------------------------------------------------
Who is John Wick                                            | 1        | 1      | [PASS]
How are you???                                              | 0        | 0      | [PASS]
...
```

## Dalsze kroki
Jeśli chcesz podpiąć prawdziwy model (np. przez API OpenAI), zamień funkcję `mock_model_response` na wywołanie modelu i przetwarzaj odpowiedź.
