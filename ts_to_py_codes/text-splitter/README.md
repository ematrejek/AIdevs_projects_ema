# Text Splitter

Narzędzie do dzielenia tekstu na mniejsze fragmenty (chunki) z zachowaniem kontekstu i generowania statystyk.

## Opis

Text Splitter to aplikacja Python, która:
- Przetwarza pliki markdown
- Dzieli tekst na mniejsze fragmenty o określonym rozmiarze
- Generuje statystyki dotyczące podziału tekstu
- Zapisuje wyniki w formacie JSON

## Wymagania

- Python 3.x
- Zależności z pliku requirements.txt

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Użycie

1. Umieść pliki markdown w tym samym katalogu co skrypt
2. Uruchom skrypt:
```bash
python app.py
```

## Wyniki

Dla każdego pliku markdown skrypt generuje:
- Plik JSON zawierający podzielone fragmenty tekstu
- Statystyki w konsoli zawierające:
  - Średni rozmiar chunka
  - Medianę rozmiaru chunka
  - Minimalny rozmiar chunka
  - Maksymalny rozmiar chunka
  - Całkowitą liczbę chunków

## Struktura projektu

```
text-splitter/
├── app.py           # Główny skrypt
├── text_service.py  # Serwis do dzielenia tekstu
├── requirements.txt # Zależności projektu
└── README.md       # Ten plik
``` 