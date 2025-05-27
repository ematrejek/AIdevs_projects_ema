import os
import json
from pathlib import Path
from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime

class MemoryService:
    def __init__(self, path: str, openai_service):
        self.path = Path(path)
        self.openai_service = openai_service
        self.path.mkdir(parents=True, exist_ok=True)
        self.memories = []
        self.memory_file = "memories.json"
        self.load_memories()

    def load_memories(self):
        try:
            print("Próba wczytania wspomnień z pliku:", self.memory_file)
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                print("Wczytano wspomnienia:", self.memories)
            else:
                print("Plik wspomnień nie istnieje, tworzę nowy")
                self.memories = []
        except Exception as e:
            print(f"Błąd podczas wczytywania wspomnień: {e}")
            self.memories = []

    async def recall(self, queries: List[str]) -> List[str]:
        """
        Przywołuje wspomnienia na podstawie zapytań.
        """
        try:
            memories = []
            print("Rozpoczynam wyszukiwanie wspomnień dla zapytań:", queries)
            
            # Sprawdź plik memories.json
            if os.path.exists(self.memory_file):
                print("Znaleziono plik memories.json")
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                    print("Wczytane wspomnienia z pliku:", memory_data)
                    
                    # Najpierw sprawdź czy jest zapytanie o imię
                    is_name_query = any(word in ' '.join(queries).lower() for word in ["imię", "nazywasz", "nazywam", "jak masz"])
                    
                    for memory in memory_data:
                        memory_content = memory["content"].lower()
                        
                        # Jeśli to zapytanie o imię, szukaj specyficznie informacji o imieniu
                        if is_name_query:
                            if any(phrase in memory_content for phrase in ["mam na imię", "nazywam się", "imię to"]):
                                print(f"Znaleziono wspomnienie o imieniu: {memory['content']}")
                                memories.append(memory["content"])
                                continue
                        
                        # Standardowe wyszukiwanie dla innych zapytań
                        for query in queries:
                            clean_query = self._prepare_text_for_matching(query)
                            clean_content = self._prepare_text_for_matching(memory_content)
                            
                            print(f"Porównuję zapytanie '{clean_query}' z treścią '{clean_content}'")
                            
                            if self._is_match(clean_query, clean_content):
                                print(f"Znaleziono pasujące wspomnienie: {memory['content']}")
                                memories.append(memory["content"])
                                break

            # Sprawdź pliki w katalogu
            print("Sprawdzam pliki w katalogu:", self.path)
            for memory_file in self.path.glob("*.json"):
                print(f"Sprawdzam plik: {memory_file}")
                with open(memory_file, "r", encoding="utf-8") as f:
                    memory_data = json.load(f)
                    memory_content = memory_data["content"].lower()
                    
                    # Najpierw sprawdź czy jest zapytanie o imię
                    is_name_query = any(word in ' '.join(queries).lower() for word in ["imię", "nazywasz", "nazywam", "jak masz"])
                    
                    if is_name_query:
                        if any(phrase in memory_content for phrase in ["mam na imię", "nazywam się", "imię to"]):
                            print(f"Znaleziono wspomnienie o imieniu: {memory_data['content']}")
                            memories.append(memory_data["content"])
                            continue
                    
                    # Standardowe wyszukiwanie dla innych zapytań
                    for query in queries:
                        clean_query = self._prepare_text_for_matching(query)
                        clean_content = self._prepare_text_for_matching(memory_content)
                        
                        print(f"Porównuję zapytanie '{clean_query}' z treścią '{clean_content}'")
                        
                        if self._is_match(clean_query, clean_content):
                            print(f"Znaleziono pasujące wspomnienie: {memory_data['content']}")
                            memories.append(memory_data["content"])
                            break

            print("Znalezione wspomnienia:", memories)
            return memories
        except Exception as e:
            print(f"Błąd podczas przywoływania wspomnień: {e}")
            return []

    def _prepare_text_for_matching(self, text: str) -> str:
        """
        Przygotowuje tekst do porównania poprzez:
        - usunięcie znaków specjalnych
        - zamianę na małe litery
        - usunięcie nadmiarowych spacji
        """
        # Zamień na małe litery i usuń znaki specjalne
        cleaned = ''.join(c.lower() for c in text if c.isalnum() or c.isspace())
        # Usuń nadmiarowe spacje
        result = ' '.join(cleaned.split())
        print(f"Przygotowany tekst do porównania: '{text}' -> '{result}'")
        return result

    def _is_match(self, query: str, content: str) -> bool:
        """
        Sprawdza czy zapytanie pasuje do treści.
        """
        # Podziel zapytanie na słowa kluczowe
        keywords = query.split()
        
        # Jeśli zapytanie jest puste, zwróć False
        if not keywords:
            print("Puste zapytanie, zwracam False")
            return False
            
        # Sprawdź czy wszystkie słowa kluczowe występują w treści
        # lub czy treść zawiera zapytanie jako całość
        # lub czy zapytanie zawiera treść jako całość
        result = (
            all(keyword in content for keyword in keywords) or
            query in content or
            content in query
        )
        print(f"Wynik dopasowania dla '{query}' i '{content}': {result}")
        return result

    async def save_memory(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Zapisuje nowe wspomnienie.
        """
        try:
            print("Próba zapisania wspomnienia:", content)
            if metadata is None:
                metadata = {}
            
            memory_id = str(uuid4())
            memory_data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            memory_file = self.path / f"{memory_id}.json"
            with open(memory_file, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            self.memories.append(memory_data)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
            
            print("Wspomnienie zapisane pomyślnie")
            return True
        except Exception as e:
            print(f"Błąd podczas zapisywania wspomnienia: {e}")
            return False

    async def sync_memories(self) -> Dict[str, Any]:
        """
        Synchronizuje wspomnienia z zewnętrznym źródłem.
        """
        try:
            # W przyszłości można dodać synchronizację z zewnętrznym źródłem
            return {
                "status": "success",
                "message": "Wspomnienia zsynchronizowane",
                "details": {
                    "synced_count": len(list(self.path.glob("*.json"))),
                    "errors": []
                }
            }
        except Exception as e:
            print(f"Błąd podczas synchronizacji wspomnień: {e}")
            return {
                "status": "error",
                "message": str(e),
                "details": {
                    "synced_count": 0,
                    "errors": [str(e)]
                }
            }

    async def get_memories(self):
        print("Zwracam wszystkie wspomnienia:", self.memories)
        return self.memories

    async def clear_memories(self):
        try:
            print("Czyszczenie wszystkich wspomnień")
            self.memories = []
            if os.path.exists(self.memory_file):
                os.remove(self.memory_file)
            print("Wspomnienia wyczyszczone pomyślnie")
            return True
        except Exception as e:
            print(f"Błąd podczas czyszczenia wspomnień: {e}")
            return False 