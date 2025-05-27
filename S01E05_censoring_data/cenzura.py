import requests
import json
import re
from typing import Dict
import time

API_KEY = "8eed1983-ee32-479e-8c44-eb85077a62e8"
DATA_URL = f"https://c3ntrala.ag3nts.org/data/{API_KEY}/cenzura.txt"
REPORT_URL = "https://c3ntrala.ag3nts.org/report"

def pobierz_dane() -> str:
    """Pobiera dane z pliku cenzura.txt."""
    try:
        print(f"Próba pobrania danych z: {DATA_URL}")
        response = requests.get(DATA_URL)
        response.raise_for_status()
        
        print(f"Status odpowiedzi: {response.status_code}")
        print(f"Nagłówki odpowiedzi: {response.headers}")
        
        # Pobierz dane bezpośrednio z odpowiedzi
        dane = response.text.strip()
        if not dane:
            raise ValueError("Otrzymano pustą odpowiedź")
            
        return dane
        
    except requests.RequestException as e:
        raise Exception(f"Błąd podczas pobierania danych: {str(e)}")
    except Exception as e:
        raise Exception(f"Nieoczekiwany błąd: {str(e)}")

def cenzuruj_dane(tekst: str) -> str:
    """Cenzuruje wrażliwe dane w tekście."""
    try:
        # Cenzurowanie imienia i nazwiska
        tekst = re.sub(r'Dane podejrzanego: [^.]*\.', 'Dane podejrzanego: CENZURA.', tekst)
        
        # Cenzurowanie miasta
        tekst = re.sub(r'Adres: [^,]*', 'Adres: CENZURA', tekst)
        
        # Cenzurowanie ulicy i numeru domu
        tekst = re.sub(r'ul\. [^.]*\.', 'ul. CENZURA.', tekst)
        
        # Cenzurowanie wieku
        tekst = re.sub(r'Wiek: \d+ lat', 'Wiek: CENZURA lat', tekst)
        
        return tekst
    except Exception as e:
        raise Exception(f"Błąd podczas cenzurowania danych: {str(e)}")

def wyslij_odpowiedz(ocenzurowany_tekst: str) -> Dict:
    """Wysyła ocenzurowane dane do API."""
    try:
        payload = {
            "task": "CENZURA",
            "apikey": API_KEY,
            "answer": ocenzurowany_tekst
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"Wysyłam payload: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(REPORT_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Błąd podczas wysyłania odpowiedzi: {str(e)}")
    except Exception as e:
        raise Exception(f"Nieoczekiwany błąd podczas wysyłania odpowiedzi: {str(e)}")

def main():
    while True:
        try:
            # Pobierz dane
            dane = pobierz_dane()
            print(f"Pobrane dane: {dane}")
            
            # Cenzuruj dane
            ocenzurowane_dane = cenzuruj_dane(dane)
            print(f"Ocenzurowane dane: {ocenzurowane_dane}")
            
            # Wyślij odpowiedź
            odpowiedz = wyslij_odpowiedz(ocenzurowane_dane)
            print(f"Odpowiedź z serwera: {odpowiedz}")
            
            # Czekaj 60 sekund przed następnym pobraniem
            print("Czekam 60 sekund przed następnym pobraniem...")
            time.sleep(60)
            
        except Exception as e:
            print(f"Wystąpił błąd: {str(e)}")
            print("Ponowna próba za 5 sekund...")
            time.sleep(5)

if __name__ == "__main__":
    main() 