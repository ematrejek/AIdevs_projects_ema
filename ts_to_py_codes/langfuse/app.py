from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from chat_service import ChatService
from langfuse_service import LangfuseService

app = FastAPI()
chat_service = ChatService()
langfuse_service = LangfuseService()

class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    conversation_id: Optional[str] = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    trace = langfuse_service.create_trace(
        id=str(uuid.uuid4()),
        name="Chat",
        session_id=conversation_id
    )

    try:
        all_messages = [
            {"role": "system", "content": "You are a helpful assistant.", "name": "Alice"},
            *[msg.dict() for msg in request.messages]
        ]
        
        generated_messages = []

        # Main Completion
        main_span = langfuse_service.create_span(trace, "Main Completion", all_messages)
        main_completion = await chat_service.completion(all_messages, "gpt-4")
        langfuse_service.finalize_span(main_span, "Main Completion", all_messages, main_completion)
        main_message = main_completion.choices[0].message
        all_messages.append(main_message)
        generated_messages.append(main_message)

        # Secondary Completion
        secondary_messages = [{"role": "user", "content": "Please say 'completion 2'"}]
        secondary_span = langfuse_service.create_span(trace, "Secondary Completion", secondary_messages)
        secondary_completion = await chat_service.completion(secondary_messages, "gpt-4")
        langfuse_service.finalize_span(secondary_span, "Secondary Completion", secondary_messages, secondary_completion)
        secondary_message = secondary_completion.choices[0].message
        generated_messages.append(secondary_message)

        # Third Completion
        third_messages = [{"role": "user", "content": "Please say 'completion 3'"}]
        third_span = langfuse_service.create_span(trace, "Third Completion", third_messages)
        third_completion = await chat_service.completion(third_messages, "gpt-4")
        langfuse_service.finalize_span(third_span, "Third Completion", third_messages, third_completion)
        third_message = third_completion.choices[0].message
        generated_messages.append(third_message)

        # Finalize trace
        await langfuse_service.finalize_trace(trace, request.messages, generated_messages)

        return {
            "completion": main_completion.choices[0].message.content,
            "completion2": secondary_completion.choices[0].message.content,
            "completion3": third_completion.choices[0].message.content,
            "conversation_id": conversation_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 