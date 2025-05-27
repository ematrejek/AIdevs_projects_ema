from typing import Dict, Any

class TextSplitter:
    async def document(self, text: str, model: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'text': text,
            'metadata': metadata
        } 