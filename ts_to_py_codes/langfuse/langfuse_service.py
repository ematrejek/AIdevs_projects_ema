from langfuse import Langfuse
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class LangfuseService:
    def __init__(self):
        self.client = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )

    def create_trace(self, id: str, name: str, session_id: str):
        return self.client.trace(
            id=id,
            name=name,
            session_id=session_id
        )

    def create_span(self, trace, name: str, messages: List[Dict[str, Any]]):
        return trace.span(
            name=name,
            input=messages
        )

    def finalize_span(self, span, name: str, input_messages: List[Dict[str, Any]], output):
        span.end(
            name=name,
            input=input_messages,
            output=output
        )

    async def finalize_trace(self, trace, input_messages: List[Dict[str, Any]], output_messages: List[Dict[str, Any]]):
        trace.update(
            input=input_messages,
            output=output_messages
        )

    async def shutdown_async(self):
        await self.client.shutdown() 