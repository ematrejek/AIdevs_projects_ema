from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from OpenAIService import OpenAIService
from MemoryService import MemoryService
from AssistantService import AssistantService
from prompts import defaultKnowledge as knowledge, memory_structure
from pydantic import BaseModel
import uvicorn

app = FastAPI()

openai_service = OpenAIService()
memory_service = MemoryService('memory/memories', openai_service)
assistant_service = AssistantService(openai_service, memory_service)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    conversation_id: str | None = None

@app.post('/api/chat')
async def chat_endpoint(request: Request, body: ChatRequest):
    messages = [msg.dict() for msg in body.messages if msg.role != 'system']
    conversation_id = body.conversation_id or str(uuid4())
    
    try:
        queries = await assistant_service.extract_queries(messages)
        memories = await memory_service.recall(queries)
        should_learn = await assistant_service.should_learn(messages, memories)
        learnings = await assistant_service.learn(messages, should_learn, memories)
        answer = await assistant_service.answer({
            'messages': messages,
            'memories': memories,
            'knowledge': knowledge,
            'learnings': learnings,
            'memory_structure': memory_structure
        })
        return JSONResponse({**answer, 'conversation_id': conversation_id})
    except Exception as e:
        print('Error in chat processing:', e)
        raise HTTPException(status_code=500, detail='An error occurred while processing your request')

@app.post('/api/sync')
async def sync_endpoint():
    try:
        changes = await memory_service.sync_memories()
        return JSONResponse(changes)
    except Exception as e:
        print('Error in memory synchronization:', e)
        raise HTTPException(status_code=500, detail='An error occurred while syncing memories')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000) 