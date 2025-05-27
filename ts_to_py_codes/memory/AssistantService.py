from prompts import (
    extract_search_queries_prompt,
    should_learn_prompt,
    learn_prompt,
    update_memory_prompt,
    memory_structure,
    default_knowledge
)

class AssistantService:
    def __init__(self, openai_service, memory_service):
        self.openai_service = openai_service
        self.memory_service = memory_service

    async def extract_queries(self, messages, trace=None):
        print("Wyodrębnianie zapytań z wiadomości:", messages)
        try:
            # Sprawdź czy to zapytanie o imię
            last_message = messages[-1]["content"].lower() if messages else ""
            is_name_query = any(word in last_message for word in ["imię", "nazywasz", "nazywam", "jak masz"])
            
            if is_name_query:
                print("Wykryto zapytanie o imię")
                return ["imię", "nazwa", "użytkownik"]
            
            # Dla innych zapytań użyj OpenAI
            response = await self.openai_service.completion([
                {"role": "system", "content": extract_search_queries_prompt(memory_structure, default_knowledge)},
                *messages
            ])
            
            # Przetwórz odpowiedź na listę zapytań
            content = response["choices"][0]["message"]["content"]
            print("Odpowiedź od OpenAI:", content)
            
            # Usuń myślniki i inne znaki specjalne
            content = content.replace("-", "").replace("*", "").strip()
            # Podziel na słowa kluczowe i usuń puste
            queries = [query.strip() for query in content.split(",") if query.strip()]
            
            # Jeśli nie znaleziono żadnych słów kluczowych, użyj oryginalnego zapytania
            if not queries and messages:
                # Usuń znaki zapytania i wykrzykniki
                clean_message = last_message.replace("?", "").replace("!", "").strip()
                queries = [clean_message]
            
            print("Wyodrębnione zapytania:", queries)
            return queries
        except Exception as e:
            print(f"Błąd podczas wyodrębniania zapytań: {e}")
            return []

    async def should_learn(self, messages, memories, trace=None):
        try:
            print("Sprawdzanie czy warto zapamiętać informacje z:", messages)
            response = await self.openai_service.completion([
                {"role": "system", "content": should_learn_prompt(memory_structure, default_knowledge, memories)},
                *messages
            ])
            should_learn = "tak" in response["choices"][0]["message"]["content"].lower()
            print("Czy warto zapamiętać:", should_learn)
            return should_learn
        except Exception as e:
            print(f"Błąd podczas oceny czy uczyć: {e}")
            return False

    async def learn(self, messages, should_learn, memories, trace=None):
        if not should_learn:
            print("Nie zapamiętuję - brak wartościowych informacji")
            return []
        try:
            print("Próba zapamiętania informacji z:", messages)
            response = await self.openai_service.completion([
                {"role": "system", "content": learn_prompt(memory_structure, default_knowledge, memories)},
                *messages
            ])
            content = response["choices"][0]["message"]["content"]
            print("Zapamiętywana informacja:", content)
            # Zapisz wspomnienie
            success = await self.memory_service.save_memory(content)
            print("Czy zapisano wspomnienie:", success)
            return [content]
        except Exception as e:
            print(f"Błąd podczas uczenia: {e}")
            return []

    async def answer(self, data, trace=None):
        try:
            messages = data["messages"]
            memories = data["memories"]
            knowledge = data["knowledge"]
            learnings = data["learnings"]

            print("Wspomnienia używane w odpowiedzi:", memories)
            print("Nowe informacje:", learnings)

            system_prompt = f"""Jesteś pomocnym asystentem. 
            Wiedza domyślna: {knowledge}
            Wspomnienia: {memories}
            Nowe informacje: {learnings}
            Odpowiadaj w języku polskim, uwzględniając zapamiętane informacje."""

            return await self.openai_service.completion([
                {"role": "system", "content": system_prompt},
                *messages
            ])
        except Exception as e:
            print(f"Błąd podczas generowania odpowiedzi: {e}")
            return {"choices": [{"message": {"content": "Przepraszam, wystąpił błąd podczas generowania odpowiedzi."}}]} 