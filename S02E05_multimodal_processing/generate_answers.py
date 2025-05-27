import json
import openai
from dotenv import load_dotenv
import os
import requests

# Załaduj zmienne środowiskowe
load_dotenv()

# Inicjalizacja OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_processed_content():
    """Ładuje przetworzone dane z pliku JSON"""
    with open('data/processed_content.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_questions():
    """Ładuje pytania z pliku tekstowego"""
    with open('data/questions.txt', 'r', encoding='utf-8') as f:
        return f.read()

def summarize_content(content):
    """Generuje skrócone podsumowanie artykułu"""
    # Ogranicz długość tekstu do pierwszych 3000 znaków
    text = content['text'][:3000]
    
    prompt = f"""
    Stwórz bardzo krótkie podsumowanie (max 500 znaków) poniższego tekstu, zachowując tylko najważniejsze fakty, daty i nazwiska.
    
    Tekst:
    {text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś asystentem tworzącym bardzo zwięzłe podsumowania."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )
    
    return response.choices[0].message.content

def generate_answers(content, questions):
    """Generuje odpowiedzi na pytania używając GPT-4"""
    # Wygeneruj skrócone podsumowanie
    summarized_text = summarize_content(content)
    
    # Ogranicz liczbę obrazów do 1 najważniejszego
    images = content['images'][:1]
    
    # Przygotuj kontekst
    context = f"""
    Tekst: {summarized_text}
    Obrazy: {json.dumps(images, ensure_ascii=False)}
    """
    
    prompt = f"""
    Odpowiedz na pytania na podstawie tekstu. Odpowiedzi powinny być krótkie (1 zdanie).
    Jeśli informacja nie jest dostępna, napisz "Informacja nie jest dostępna w tekście".
    
    Kontekst: {context}
    Pytania: {questions}
    
    Format odpowiedzi (JSON):
    {{
        "task": "arxiv",
        "apikey": "8eed1983-ee32-479e-8c44-eb85077a62e8",
        "answer": {{
            "01": "odpowiedź",
            "02": "odpowiedź",
            "03": "odpowiedź",
            "04": "odpowiedź",
            "05": "odpowiedź"
        }}
    }}
    """
    
    # Wygeneruj odpowiedzi
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś asystentem analizującym tekst i odpowiadającym na pytania w zwięzły sposób."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def main():
    try:
        # Załaduj dane
        content = load_processed_content()
        questions = load_questions()
        
        # Wygeneruj odpowiedzi
        answers = generate_answers(content, questions)
        
        # Zapisz odpowiedzi do pliku
        with open('data/answers.json', 'w', encoding='utf-8') as f:
            f.write(answers)
            
        # Wyślij odpowiedzi na endpoint
        response = requests.post(
            "https://c3ntrala.ag3nts.org/report",
            json=json.loads(answers)
        )
        
        if response.status_code == 200:
            print("Odpowiedzi zostały wygenerowane, zapisane i wysłane pomyślnie")
        else:
            print(f"Błąd podczas wysyłania odpowiedzi: {response.status_code}")
            print(f"Treść odpowiedzi: {response.text}")
        
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    main() 