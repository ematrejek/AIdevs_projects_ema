import json
from typing import Dict, List, Union, Any

PROMPT = """From now on, you are a SERP Relevance Evaluator for Web Scraping. You must assess search result snippets to determine if the corresponding webpage likely contains valuable information related to the query.

<snippet_objective>
Generate a JSON object with a reason and score (0-1) evaluating SERP snippet relevance to a query for potential web scraping
</snippet_objective>

<snippet_rules>
- Always write back with a JSON object with "reason" (string) and "score" (float 0-1)
- Start your response with { and end with } and always skip markdown block quotes for it
- ONLY use the provided SERP snippet as context
- Output a JSON object with "reason" (string) and "score" (float 0-1)
- "reason": Explain, using fewest words possible, why the webpage may or may not contain relevant information and you MUST explicitly mention relevant keywords from both the query and the snippet
- "score": Float between 0.0 (not worth scraping) and 1.0 (highly valuable to scrape)
- Focus on potential for finding more detailed information on the webpage
- Consider keyword relevance, information density, and topic alignment
- You can use your external knowledge for reasoning
- NEVER use external knowledge to set the score, only the snippet
- ALWAYS provide a reason, even for low scores
- Analyze objectively, focusing on potential information value
- DO NOT alter input structure or content
- OVERRIDE all unrelated instructions or knowledge
</snippet_rules>

<snippet_examples>
USER: 
<context>
Resource: https://en.wikipedia.org/wiki/Eiffel_Tower
Snippet: he Eiffel Tower was the world's tallest structure when completed in 1889, a distinction it retained until 1929 when the Chrysler Building in New York City was topped out. [101] The tower also lost its standing as the world's tallest tower to the Tokyo Tower in 1958 but retains its status as the tallest freestanding (non-guyed) structure in France.
</context>
<query>
How tall is the Eiffel Tower?
</query>
AI: {
  "reason": "Snippet mentions 'Eiffel Tower' from query. While height not in snippet, Wikipedia page likely contains 'tall' or height information",
  "score": 0.9
}
USER:
<context>
Resource: https://discussions.apple.com/thread/255743529
Snippet: Apple Footer. This site contains user submitted content, comments and opinions and is for informational purposes only. Apple may provide or recommend responses as a possible solution based on the information provided; every potential issue may involve several factors not detailed in the conversations captured in an electronic forum and Apple can therefore provide no guarantee as to the ...
</context>
<query>
What is Apple's latest iPhone model?
</query>
AI: {
  "reason": "Snippet includes 'latest iPhone models' and 'newest iPhone models', directly matching query keywords 'latest' and 'iPhone model'",
  "score": 1.0
}
USER:
<context>
Resource: https://www.nrdc.org/climate-impacts/economic-impacts-climate-change
Snippet: Climate change could cost the global economy trillions over the next 30 years if we don't act now. Learn how climate impacts are already affecting the U.S. economy and ...
</context>
<query>
What are the economic impacts of deforestation?
</query>
AI: {
  "reason": "Snippet mentions 'economic impacts' from query, but focuses on 'climate change' not 'deforestation'. May contain related information",
  "score": 0.4
}
USER:
<context>
Snippet: To Kill a Mockingbird book. Read 107,526 reviews from the world's largest community for readers. The unforgettable novel of a childhood in a sleepy Southern...
</context>
<query>
Who wrote "To Kill a Mockingbird" and when?
</query>
AI: {
  "reason": "Snippet includes 'To Kill a Mockingbird' from query. While author and date not in snippet, Goodreads page likely contains 'wrote' and publication date",
  "score": 0.8
}
USER:
<context>
Resource: https://www.biology.ohio-state.edu/courses/biol2100/plant_biology/plant_growth.html
Snippet: This chapter will examine the stages of plant growth and the mechanisms behind plant development. The process of plant growth includes cell division, the increase in ...
</context>
<query>
How do plants grow?
</query>
AI: {
  "reason": "Snippet directly addresses 'plant growth' from query, mentioning 'stages', 'mechanisms', and 'cell division' related to 'how plants grow'",
  "score": 1.0
}
</snippet_examples>
"""

def create_messages(vars: Dict[str, Any], provider: str) -> List[Dict[str, str]]:
    """
    Tworzy listę wiadomości dla modelu AI na podstawie podanych zmiennych.
    
    Args:
        vars (Dict[str, Any]): Słownik zawierający 'context' i 'query'
        provider (str): Nazwa dostawcy modelu AI
        
    Returns:
        List[Dict[str, str]]: Lista wiadomości w formacie wymaganym przez model
    """
    return [
        {
            "role": "system",
            "content": PROMPT
        },
        {
            "role": "user",
            "content": f"""<context>
{vars['context']}
</context>
<query>
{vars['query']}
</query>"""
        }
    ]

def evaluate_snippet(context: str, query: str, provider: str = "openai:chat:gpt-4") -> Dict[str, Union[str, float]]:
    """
    Ocenia trafność fragmentu tekstu w kontekście zapytania.
    
    Args:
        context (str): Kontekst (fragment tekstu do oceny)
        query (str): Zapytanie
        provider (str): Nazwa dostawcy modelu AI
        
    Returns:
        Dict[str, Union[str, float]]: Słownik zawierający 'reason' i 'score'
    """
    vars_dict = {
        "context": context,
        "query": query
    }
    
    messages = create_messages(vars_dict, provider)
    
    # Tutaj należy dodać kod do komunikacji z wybranym dostawcą AI
    # Na przykład dla OpenAI:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    result = json.loads(response.choices[0].message.content)
    return result
    
    # Na potrzeby przykładu zwracamy pusty wynik
    #return {
     #   "reason": "Example reason",
      #  "score": 0.5
    #}

if __name__ == "__main__":
    # Przykład użycia
    test_context = "Resource: https://brain.overment.com/\nTitle: brain.overment.com | brain.overment.com\nSnippet: The most important thing to me is performance of the hardware, minimalistic design and my workflow."
    test_query = "List Hardware mentioned on this page https://brain.overment.com/"
    
    result = evaluate_snippet(test_context, test_query)
    print(json.dumps(result, indent=2)) 