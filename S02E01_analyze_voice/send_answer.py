import requests
import json

def send_answer():
    url = "https://c3ntrala.ag3nts.org/report"
    
    payload = {
        "task": "mp3",
        "apikey": "8eed1983-ee32-479e-8c44-eb85077a62e8",
        "answer": "Łojasiewicza"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    send_answer() 