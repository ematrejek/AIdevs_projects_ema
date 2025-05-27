from typing import List, Dict, Any
import numpy as np
from OpenAIService import OpenAIService


class VectorService:
    def __init__(self, openai_service: OpenAIService):
        # 1. Inicjalizacja serwisu:
        # - przyjmuje instancję OpenAIService do tworzenia embeddingów
        # - tworzy pusty słownik na kolekcje tekstów
        self.openai_service = openai_service
        self.collections = {}
    
    async def initialize_collection_with_data(self, collection_name: str, points: List[Dict[str, Any]]):
        # 2. Dodawanie nowej kolekcji tekstów:
        # - przyjmuje nazwę kolekcji i listę punktów (tekstów)
        # - zapisuje teksty w słowniku pod podaną nazwą
        self.collections[collection_name] = points
    
    async def perform_search(self, collection_name: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # 3. Wyszukiwanie podobnych tekstów:
        # - zamienia tekst zapytania na wektor liczbowy (embedding)
        query_embedding = await self.openai_service.create_embedding(query)
        
        # - pobiera kolekcję tekstów do przeszukania
        collection = self.collections.get(collection_name, [])
        
        # - dla każdego tekstu w kolekcji:
        results = []
        for point in collection:
            # -- zamienia tekst na wektor
            point_embedding = await self.openai_service.create_embedding(point['text'])
            # -- oblicza podobieństwo między wektorami
            similarity = self._cosine_similarity(query_embedding, point_embedding)
            # -- zapisuje tekst i jego podobieństwo
            results.append({
                'payload': point,
                'score': similarity
            })
        
        # - sortuje wyniki malejąco według podobieństwa
        # - zwraca określoną liczbę najbardziej podobnych tekstów
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        # 4. Obliczanie podobieństwa kosinusowego między dwoma wektorami:
        # - konwertuje listy na tablice numpy
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        # - oblicza i zwraca podobieństwo kosinusowe
        # - wynik 1 oznacza identyczne wektory, 0 oznacza brak podobieństwa
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))