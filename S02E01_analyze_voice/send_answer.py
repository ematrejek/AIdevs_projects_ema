import requests
import json

def send_answer():
    url = "https://c3ntrala.ag3nts.org/report"
    
    payload = {
        "task": "mp3",
        "apikey": API_KEY = "xxx", ## API do platformy AI devs
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
