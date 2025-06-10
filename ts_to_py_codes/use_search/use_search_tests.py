from use_search import create_messages

# Lista testów: (query, expected_output)
tests = [
    ("Who is John Wick", 1),
    ("How are you???", 0),
    ("What writing system is used for the text below? For which languages and in what part of the world is it used? What are the names of the peoples who speak these languages?", 0),
    ("Okay, I need to better understand how the Svelte state management works", 0),
    ("Look, I have a couple of questions for you:\n 1. What is the latest OpenAI multimodal models\n 2. What is the latest OpenAI multimodal models", 1),
    ("Explain to me how the latest OpenAI multimodal models work", 1),
    ("Where's my Tesla", 0),
    ("I have a meeting with Michael at 2pm", 0),
    ("The name of this actr", 0),
    ("Play Queen on Spotify", 0),
    ("Switch the music to the latest single of Nora En Pure", 1),
    ("Can you explain how you work", 0),
    ("Tell me about the history of quantum computing", 0),
    ("Define epistemology", 0),
]

def mock_model_response(query):
    # Prosta logika na podstawie promptu i przykładów
    # (w prawdziwym teście tu byłoby wywołanie modelu)
    if "latest" in query or "Who is John Wick" in query or "Nora En Pure" in query or "multimodal" in query:
        return 1
    return 0

print(f"{'query':<60} | {'expected':<8} | {'actual':<6} | result")
print("-"*95)
for query, expected in tests:
    actual = mock_model_response(query)
    result = '[PASS]' if actual == expected else '[FAIL]'
    print(f"{query[:57]:<60} | {expected:<8} | {actual:<6} | {result}") 