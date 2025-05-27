import requests
import json

def test_chat():
    url = "http://localhost:3000/api/chat"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Cześć, jak się masz?"
            }
        ]
    }
    
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_chat() 