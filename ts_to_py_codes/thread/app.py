from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
import uvicorn

load_dotenv()

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: Message

class Conversation:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.summary: str = ""

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

    def update_summary(self, summary: str):
        self.summary = summary

conversation = Conversation()

class LLMHandler:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4" # Można zmienić na "gpt-4o" lub inny preferowany

    def get_completion(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in OpenAI API call: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def create_system_prompt(self) -> Dict[str, str]:
        return {
            "role": "system",
            "content": f"""You are Alice, a helpful assistant who speaks using as few words as possible.
                        {f'''Here is a summary of the conversation so far:
                        <conversation_summary>{conversation.summary}</conversation_summary>''' if conversation.summary else ''}
                        Let's chat!"""
        }

    def generate_summarization(self, user_message_content: str, assistant_response_content: str) -> str:
        prompt = f"""Please summarize the following conversation turn in a concise manner, incorporating the previous summary if available:
<previous_summary>{conversation.summary or "No previous summary"}</previous_summary>
<current_turn>
User: {user_message_content}
Assistant: {assistant_response_content}
</current_turn>
New concise summary:"""

        messages_for_summarization = [
            # Można by tu użyć innego, dedykowanego promptu systemowego dla samego zadania podsumowania,
            # ale dla prostoty użyjemy tylko bezpośredniego polecenia.
            {"role": "user", "content": prompt}
        ]
        
        # Można rozważyć użycie tańszego/szybszego modelu do samego podsumowania
        return self.get_completion(messages_for_summarization)

llm = LLMHandler()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Dodaj wiadomość użytkownika do pełnej historii konwersacji (nadal potrzebne do logiki podsumowania)
        conversation.add_message(request.message.role, request.message.content)
        
        # Przygotuj listę wiadomości dla LLM: prompt systemowy + bieżąca wiadomość użytkownika
        # Zamiast `request.message.dict()` można też jawnie stworzyć słownik:
        # current_user_message_dict = {"role": request.message.role, "content": request.message.content}
        # Poniżej używamy metody .model_dump() dla Pydantic v2 lub .dict() dla v1
        # Dla uproszczenia i kompatybilności, stworzymy słownik jawnie:
        current_user_message_dict = {"role": request.message.role, "content": request.message.content}
        
        messages_for_llm = [
            llm.create_system_prompt(),
            current_user_message_dict
        ]
        
        assistant_response_content = llm.get_completion(messages_for_llm)
        
        # Dodaj odpowiedź asystenta do pełnej historii konwersacji
        conversation.add_message("assistant", assistant_response_content)

        # Zaktualizuj podsumowanie konwersacji na podstawie bieżącej wymiany i poprzedniego podsumowania
        conversation.update_summary(llm.generate_summarization(
            request.message.content, # Treść wiadomości użytkownika
            assistant_response_content # Treść odpowiedzi asystenta
        ))
        
        return {"content": assistant_response_content}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo")
async def demo():
    demo_messages_content = [ # Zmieniono nazwę dla jasności, że to tylko treści
        "Hi! I'm Adam",
        "How are you?",
        "Do you know my name?"
    ]

    responses = []
    # Resetuj konwersację dla czystego demo (opcjonalne, zależy od pożądanego zachowania)
    # conversation.messages = []
    # conversation.summary = ""

    for user_content in demo_messages_content:
        print(f"User: {user_content}")
        
        # Dodaj wiadomość użytkownika do pełnej historii konwersacji
        conversation.add_message("user", user_content)
        
        # Przygotuj listę wiadomości dla LLM: prompt systemowy + bieżąca wiadomość użytkownika z demo
        current_demo_user_message_dict = {"role": "user", "content": user_content}
        
        messages_for_llm = [
            llm.create_system_prompt(),
            current_demo_user_message_dict
        ]
        
        assistant_response_content = llm.get_completion(messages_for_llm)
        print(f"Assistant: {assistant_response_content}")
        responses.append(assistant_response_content)
        
        # Dodaj odpowiedź asystenta do pełnej historii konwersacji
        conversation.add_message("assistant", assistant_response_content)

        # Zaktualizuj podsumowanie konwersacji
        conversation.update_summary(llm.generate_summarization(
            user_content,
            assistant_response_content
        ))

    return {"responses": responses}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)