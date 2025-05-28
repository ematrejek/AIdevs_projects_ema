import requests
import json

API_KEY = "8xxx" ## klucz API do aidevs
API_URL = "https://c3ntrala.ag3nts.org/apidb"

def query_database(query):
    payload = {
        "task": "database",
        "apikey": API_KEY,
        "query": query
    }
    
    response = requests.post(API_URL, json=payload)
    return response.json()

# Zapytanie, które znajdzie aktywne datacenters z nieaktywnymi menedżerami
query = """
SELECT d.dc_id 
FROM datacenters d 
JOIN users u ON d.manager = u.id 
WHERE d.is_active = 1 AND u.is_active = 0;
"""

result = query_database(query)
print("\nWynik zapytania:", json.dumps(result, indent=2))

# Przygotowanie odpowiedzi do centrali
answer = {
    "task": "database",
    "apikey": API_KEY,
    "answer": [item["dc_id"] for item in result["reply"]] if result["error"] == "OK" else []
}

print("\nOdpowiedź do centrali:", json.dumps(answer, indent=2))