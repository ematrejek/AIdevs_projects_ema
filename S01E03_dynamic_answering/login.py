import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import time
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Konfiguracja OpenAI API (klucz pobierany automatycznie z env)
client = OpenAI()

def get_question():
    """Pobiera stronę i wyciąga pytanie."""
    response = requests.get("https://xyz.ag3nts.org/")
    soup = BeautifulSoup(response.text, 'html.parser')
    question_element = soup.find('p', id='human-question')
    if question_element:
        # Usuwamy "Question:" i "br" z tekstu
        question_text = question_element.get_text().replace("Question:", "").strip()
        return question_text
    return None

def get_llm_answer(question):
    """Pobiera odpowiedź od modelu LLM."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem. Odpowiadaj krótko i konkretnie, tylko liczbą."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Błąd podczas pobierania odpowiedzi z LLM: {e}")
        return None

def login(username, password, answer):
    """Wysyła żądanie logowania."""
    data = {
        'username': username,
        'password': password,
        'answer': answer
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(
        "https://xyz.ag3nts.org/",
        data=data,
        headers=headers,
        allow_redirects=True
    )
    
    return response

def main():
    username = "tester"
    password = "574e112a"
    
    while True:
        # Pobierz pytanie
        question = get_question()
        if not question:
            print("Nie udało się pobrać pytania. Próba ponownie...")
            time.sleep(2)
            continue
            
        print(f"Pytanie: {question}")
        
        # Pobierz odpowiedź od LLM
        answer = get_llm_answer(question)
        if not answer:
            print("Nie udało się pobrać odpowiedzi od LLM. Próba ponownie...")
            time.sleep(2)
            continue
            
        print(f"Odpowiedź: {answer}")
        
        # Próba logowania
        response = login(username, password, answer)
        
        # Sprawdź odpowiedź
        if response.status_code == 200:
            print("Zawartość strony:")
            print(response.text)
            break
        else:
            print(f"Błąd logowania (status: {response.status_code}). Próba ponownie...")
            time.sleep(2)

if __name__ == "__main__":
    main() 