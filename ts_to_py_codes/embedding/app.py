from OpenAIService import OpenAIService
from TextService import TextSplitter
from VectorService import VectorService

data = [
    'Apple (Consumer Electronics)',
    'Tesla (Automotive)',
    'Microsoft (Software)',
    'Google (Internet Services)',
    'Nvidia (Semiconductors)',
    'Meta (Social Media)',
    'X Corp (Social Media)',
    'Tech•sistence (Newsletter)'
]

queries = ['Car company', 'Macbooks', 'Facebook', 'Newsletter']

COLLECTION_NAME = "aidevs"

async def initialize_data():
    openai = OpenAIService()
    vector_service = VectorService(openai)
    text_splitter = TextSplitter()
    
    points = []
    # Iteruje przez każdy tekst z listy 'data'
    # Dla każdego tekstu:
    # - tworzy dokument używając text_splitter.document()
    # - przekazuje tekst, model 'gpt-4' i metadane z rolą 'embedding-test'
    # - dodaje utworzony dokument do listy points
    for text in data:
        doc = await text_splitter.document(text, 'gpt-4', {'role': 'embedding-test'})
        points.append(doc)
    
    await vector_service.initialize_collection_with_data(COLLECTION_NAME, points)
    return vector_service

async def main():
    vector_service = await initialize_data()
    
    search_results = []
    for query in queries:
        results = await vector_service.perform_search(COLLECTION_NAME, query, 3)
        search_results.append(results)
    
    for query, results in zip(queries, search_results):
        print(f"Query: {query}")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['payload']['text']} (Score: {result['score']})")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 