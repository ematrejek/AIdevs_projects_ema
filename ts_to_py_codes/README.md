# ts_to_py_codes

Ten folder zawiera przykłady implementacji API chatbotów w języku Python, które zostały przepisane z TypeScript.

## Zawartość folderu

### /files
Implementacja asystenta AI z kontekstem konwersacji, zawierająca:
- Endpoint czatu wykorzystujący GPT-4
- System zapamiętywania kontekstu i historii konwersacji
- Wyszukiwanie semantyczne z użyciem embeddingów
- Pełna dokumentacja w README.md

### /langfuse
Implementacja API czatu z integracją Langfuse, zawierająca:
- Monitoring i śledzenie interakcji z modelem językowym
- Wykonywanie trzech uzupełnień w ramach jednego żądania
- Integracja z Langfuse do analizy
- Szczegółowa dokumentacja w README.md

## Wymagania techniczne
- Python 3.x
- FastAPI
- OpenAI API
- Langfuse (dla wersji z monitoringiem)
- Pozostałe zależności znajdują się w plikach requirements.txt

## Instalacja i uruchomienie
Każdy podkatalog zawiera własne instrukcje instalacji i uruchomienia w dedykowanym pliku README.md.
