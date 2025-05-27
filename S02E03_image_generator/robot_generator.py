import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import httpx

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja
API_KEY = "8eed1983-ee32-479e-8c44-eb85077a62e8"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://c3ntrala.ag3nts.org/data"
REPORT_URL = "https://c3ntrala.ag3nts.org/report"

# Konfiguracja klienta HTTP bez proxy
http_client = httpx.Client(transport=httpx.HTTPTransport())

# Inicjalizacja klienta OpenAI
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    http_client=http_client
)

def get_robot_description():
    """Pobiera aktualny opis robota z API."""
    url = f"{BASE_URL}/{API_KEY}/robotid.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def generate_robot_image(description):
    """Generuje obraz robota używając DALL-E 3."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a detailed image of a robot with the following description: {description}. The image should be photorealistic and high quality.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        return response.data[0].url
    except Exception as e:
        print(f"Błąd podczas generowania obrazu: {str(e)}")
        raise

def send_report(image_url):
    """Wysyła raport z URL obrazu do centrali."""
    payload = {
        "task": "robotid",
        "apikey": API_KEY,
        "answer": image_url
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(REPORT_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    try:
        # Pobierz opis robota
        description = get_robot_description()
        print(f"Pobrano opis robota: {description}")
        
        # Wygeneruj obraz
        image_url = generate_robot_image(description)
        print(f"Wygenerowano obraz: {image_url}")
        
        # Wyślij raport
        result = send_report(image_url)
        print(f"Wynik wysłania raportu: {result}")
        
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    main() 