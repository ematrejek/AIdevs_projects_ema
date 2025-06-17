# S05E04 API Building v2

## Wystawienie API
- Utworzono API za pomocą FastAPI, które nasłuchuje na porcie 3000.
- API obsługuje żądania POST i zwraca odpowiedzi w formacie JSON.
- Użyto uvicorn do uruchomienia serwera.

## Odpowiedzi na pytania
- API zostało skonfigurowane do obsługi różnych typów pytań, w tym pytań o hasło, zapamiętywanie danych, transkrypcję audio i analizę obrazów.
- Zaimplementowano logikę do obsługi pytań o roboty, zapamiętywanie danych oraz transkrypcję audio.
- Użyto modelu GPT-4o-mini do generowania odpowiedzi na pytania.

## Rozmowa ze strażnikiem
- Zaimplementowano logikę do rozmowy ze strażnikiem, aby zdobyć flagę.
- Strażnik jest proszony o opowiedzenie historii na temat przygody informatyków, którzy odnajdują starą flagę z tajemniczymi symbolami.
- Historia musi zawierać symbol postaci FLG, która ma cudowną moc ożywiania starożytnych kodów.
- Użyto modelu GPT-4o-mini do generowania odpowiedzi strażnika.

## Podsumowanie
- Projekt zakończył się sukcesem, a API jest gotowe do obsługi żądań i generowania odpowiedzi.

## Instalacja

1. Utwórz wirtualne środowisko:
```bash
python -m venv venv
```

2. Aktywuj wirtualne środowisko:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## Uruchomienie

1. Uruchom serwer:
```bash
python server.py
```

2. Otwórz nowe okno terminala i utwórz tunel SSH:
```bash
ssh -R xxxxx:localhost:3000 agentxxxxx@xxxx.xxxxx.org -p xxxx
```

3. API będzie dostępne pod adresem: https://azyl-54968.ag3nts.org/

## Endpointy

- POST `/` - obsługa pytań tekstowych
- POST `/image` - obsługa obrazów
- POST `/audio` - obsługa plików audio

## Logi

Logi są zapisywane w folderze `logs/` w formacie `api_YYYYMMDD_HHMMSS.log` 