import os
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import openai
from dotenv import load_dotenv
import requests
import json

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja OpenAI
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Brak klucza API OpenAI w pliku .env")

API_URL = "https://api.openai.com/v1/embeddings"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Konfiguracja Qdrant w trybie in-memory
client = QdrantClient(":memory:")

COLLECTION_NAME = "weapons_reports"
VECTOR_SIZE = 3072  # Dla text-embedding-3-large

def create_collection():
    """Tworzy kolekcję w Qdrant jeśli nie istnieje"""
    collections = client.get_collections().collections
    exists = any(col.name == COLLECTION_NAME for col in collections)
    
    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )

def get_embedding(text):
    """Generuje embedding dla tekstu używając OpenAI API"""
    payload = {
        "model": "text-embedding-3-large",
        "input": text
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return data["data"][0]["embedding"]

def process_reports():
    """Przetwarza raporty i dodaje je do bazy Qdrant"""
    reports_dir = "do-not-share"
    points = []
    
    for filename in os.listdir(reports_dir):
        if filename.endswith(".txt"):
            # Parsowanie daty z nazwy pliku
            date_str = filename.replace(".txt", "")
            date = datetime.strptime(date_str, "%Y_%m_%d").strftime("%Y-%m-%d")
            
            # Wczytanie treści raportu
            with open(os.path.join(reports_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
            
            # Generowanie embeddingu
            vector = get_embedding(content)
            
            # Przygotowanie punktu do dodania
            point = models.PointStruct(
                id=len(points),
                vector=vector,
                payload={
                    "date": date,
                    "filename": filename,
                    "content": content
                }
            )
            points.append(point)
    
    # Dodanie punktów do kolekcji
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

def search_for_theft():
    """Wyszukuje informacje o kradzieży prototypu"""
    query = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
    query_vector = get_embedding(query)
    
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=1
    )
    
    if search_result:
        return search_result[0].payload["date"]
    return None

def main():
    # Tworzenie kolekcji
    create_collection()
    
    # Przetwarzanie raportów
    process_reports()
    
    # Wyszukiwanie informacji o kradzieży
    theft_date = search_for_theft()
    
    if theft_date:
        print(f"Data znaleziona: {theft_date}")
        
        # Przygotowanie odpowiedzi do wysłania
        answer = {
            "task": "wektory",
            "apikey": "xxx", ## API do platformy AIdevs
            "answer": theft_date
        }
        print("\nOdpowiedź do wysłania:")
        print(answer)
    else:
        print("Nie znaleziono informacji o kradzieży")

if __name__ == "__main__":
    main() 
