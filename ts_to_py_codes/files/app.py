from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
import os
from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI
from datetime import datetime

# Ładowanie zmiennych środowiskowych
load_dotenv()

app = FastAPI()
port = 3001

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    conversation_id: Optional[str] = None

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY nie jest ustawiony w zmiennych środowiskowych")
        self.client = AsyncOpenAI(api_key=api_key)

    async def create_embedding(self, input_text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-large",
                input=input_text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error in creating embedding: {e}")
            raise

    async def completion(self, messages: List[Dict[str, str]], model: str = "gpt-4", stream: bool = False, json_mode: bool = False):
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            return response
        except Exception as e:
            print(f"Error in OpenAI completion: {e}")
            raise

class ContextService:
    def __init__(self, context_dir: str, openai_service: OpenAIService):
        self.context_dir = context_dir
        self.openai_service = openai_service
        os.makedirs(context_dir, exist_ok=True)

    async def get_existing_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        try:
            file_path = os.path.join(self.context_dir, f"{conversation_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get('messages', [])
            return []
        except Exception as e:
            print(f"Error getting existing messages: {e}")
            return []

    async def search_similar_messages(self, embedding: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        # Implementacja wyszukiwania podobnych wiadomości
        return []

    async def search_similar_memories(self, embedding: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        # Implementacja wyszukiwania podobnych wspomnień
        return []

    async def get_relevant_contexts(self, similar_messages: List[Dict], similar_memories: List[Dict]) -> str:
        # Implementacja pobierania istotnych kontekstów
        return ""

    async def save_conversation(self, conversation_data: Dict[str, Any]) -> str:
        conversation_id = conversation_data.get('conversation_uuid', str(uuid.uuid4()))
        file_path = os.path.join(self.context_dir, f"{conversation_id}.json")
        with open(file_path, 'w') as f:
            json.dump(conversation_data, f)
        return conversation_id

    async def save_memory_for_conversation(self, memory: Dict[str, Any], conversation_id: str):
        # Implementacja zapisywania wspomnień
        pass

class AssistantService:
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service

    def add_system_message(self, messages: List[Dict[str, str]], context: str) -> List[Dict[str, str]]:
        system_message = {
            "role": "system",
            "content": f"Context: {context}"
        }
        return [system_message] + messages

    async def answer(self, data: Dict[str, Any]) -> str:
        try:
            response = await self.openai_service.completion(data['messages'])
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in assistant answer: {e}")
            raise

    async def learn(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        # Implementacja uczenia się z konwersacji
        return None

# Inicjalizacja serwisów
openai_service = OpenAIService()
context_service = ContextService('context', openai_service)
assistant_service = AssistantService(openai_service)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Ładowanie wiadomości z pliku pamięci lub użycie wiadomości z żądania
        thread = messages if len([m for m in messages if m['role'] != 'system']) > 1 else \
                await context_service.get_existing_messages(conversation_id) + [messages[-1]]
        
        latest_user_message = thread[-1]
        if not latest_user_message:
            raise HTTPException(status_code=400, detail="No user message provided")
        
        # Tworzenie embeddingu dla ostatniej wiadomości użytkownika
        latest_message_embedding = await openai_service.create_embedding(latest_user_message['content'])
        
        # Wyszukiwanie podobnych wiadomości i wspomnień
        similar_messages, similar_memories = await asyncio.gather(
            context_service.search_similar_messages(latest_message_embedding, 3),
            context_service.search_similar_memories(latest_message_embedding, 3)
        )
        
        # Znajdowanie istotnych kontekstów
        relevant_contexts = await context_service.get_relevant_contexts(similar_messages, similar_memories)
        thread = assistant_service.add_system_message(thread, relevant_contexts)
        
        # Generowanie odpowiedzi asystenta
        assistant_content = await assistant_service.answer({"messages": thread})
        
        # Aktualizacja wiadomości
        updated_messages = thread + [{"role": "assistant", "content": assistant_content}]
        
        # Uczenie się z konwersacji
        memory = await assistant_service.learn(updated_messages)
        
        # Zapisywanie konwersacji
        saved_conversation_id = await context_service.save_conversation({
            "messages": updated_messages,
            "keywords": memory.get('keywords', []) if memory else [],
            "conversation_uuid": conversation_id
        })
        
        # Zapisywanie wspomnień
        if memory:
            await context_service.save_memory_for_conversation(memory, saved_conversation_id)
        
        return {
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": assistant_content
                },
                "finish_reason": "stop"
            }]
        }
        
    except Exception as e:
        print(f"Error in chat processing: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")

class ConversationHistory(BaseModel):
    id: str
    first_message: str
    last_message: str
    message_count: int
    created_at: str
    keywords: List[str]

@app.get("/api/history")
async def get_history():
    try:
        conversations = []
        for filename in os.listdir(context_service.context_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(context_service.context_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = data.get('messages', [])
                    if messages:
                        # Pomijamy wiadomości systemowe
                        user_messages = [m for m in messages if m['role'] == 'user']
                        if user_messages:
                            conversations.append(ConversationHistory(
                                id=data.get('conversation_uuid', filename.replace('.json', '')),
                                first_message=user_messages[0]['content'],
                                last_message=user_messages[-1]['content'],
                                message_count=len(messages),
                                created_at=datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                                keywords=data.get('keywords', [])
                            ))
        
        # Sortujemy konwersacje od najnowszych
        conversations.sort(key=lambda x: x.created_at, reverse=True)
        return {"conversations": conversations}
    except Exception as e:
        print(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while getting conversation history")

@app.get("/api/history/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        file_path = os.path.join(context_service.context_dir, f"{conversation_id}.json")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while getting conversation")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port) 