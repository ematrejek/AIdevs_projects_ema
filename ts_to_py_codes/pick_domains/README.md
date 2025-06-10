# Pick Domains

Narzędzie do generowania zoptymalizowanych zapytań wyszukiwania na podstawie zapytania użytkownika.

## Opis

Pick Domains to narzędzie, które pomaga w generowaniu precyzyjnych, zoptymalizowanych pod kątem wyszukiwania zapytań. Wykorzystuje wstępnie zdefiniowaną listę domen i zasobów, aby generować zapytania skierowane do konkretnych źródeł informacji.

## Funkcjonalności

- Generowanie zoptymalizowanych zapytań wyszukiwania
- Automatyczne dopasowywanie zapytań do odpowiednich domen
- Wsparcie dla wielu źródeł informacji
- Generowanie zapytań w formacie JSON
- Możliwość rozbicia złożonych zapytań na proste, skoncentrowane na kluczowych słowach

## Struktura odpowiedzi

Narzędzie zwraca odpowiedź w formacie JSON zawierającą:
- `_thoughts`: Krótką analizę krok po kroku
- `queries`: Tablicę obiektów zawierających:
  - `q`: Zoptymalizowane zapytanie
  - `url`: Docelową domenę

## Przykład użycia

```python
from pick_domains import pick_domains

async def example():
    vars = {"query": "Jak zoptymalizować komponenty React?"}
    result = await pick_domains(vars, provider)
    print(result)
```

## Obsługiwane domeny

Narzędzie zawiera wstępnie zdefiniowaną listę domen, w tym:
- Dokumentacje techniczne (React, Vue, Svelte, itp.)
- Platformy edukacyjne
- Dokumentacje narzędzi deweloperskich
- Platformy społecznościowe
- I wiele innych

## Wymagania

- Python 3.6+
- Dostęp do providera AI (np. OpenAI)

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj wymagane zależności
3. Skonfiguruj provider AI

## Licencja

MIT 