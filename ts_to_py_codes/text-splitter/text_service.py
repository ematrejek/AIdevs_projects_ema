from typing import List, Dict, Any

class TextSplitter:
    def split(self, text: str, chunk_size: int) -> List[Dict[str, Any]]:
        # Podziel tekst na akapity
        paragraphs = text.split('\n\n')
        docs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Oblicz przybliżoną liczbę tokenów (słów)
            tokens = len(paragraph.split())
            
            docs.append({
                'content': paragraph,
                'metadata': {
                    'tokens': tokens
                }
            })
        
        return docs 