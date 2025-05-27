import os
import json
from pathlib import Path
from typing import List, Dict, Any
from text_service import TextSplitter

def process_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    splitter = TextSplitter()
    docs = splitter.split(text, 1000)
    
    json_file_path = Path(file_path).with_suffix('.json')
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(docs, f, indent=2)
    
    chunk_sizes = [doc['metadata']['tokens'] for doc in docs]
    avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
    min_chunk_size = min(chunk_sizes)
    max_chunk_size = max(chunk_sizes)
    median_chunk_size = sorted(chunk_sizes)[len(chunk_sizes) // 2]
    
    return {
        'file': os.path.basename(file_path),
        'avgChunkSize': f"{avg_chunk_size:.2f}",
        'medianChunkSize': median_chunk_size,
        'minChunkSize': min_chunk_size,
        'maxChunkSize': max_chunk_size,
        'totalChunks': len(chunk_sizes)
    }

def main():
    # Get all markdown files in the current directory
    directory_path = Path(__file__).parent
    reports = []
    
    for file in directory_path.glob('*.md'):
        report = process_file(str(file))
        reports.append(report)
    
    # Print reports in a table-like format
    if reports:
        headers = reports[0].keys()
        print("\n".join([
            " | ".join(headers),
            "-" * sum(len(h) + 3 for h in headers)
        ]))
        for report in reports:
            print(" | ".join(str(report[h]) for h in headers))

if __name__ == "__main__":
    main() 