import os
import json
import requests
from bs4 import BeautifulSoup
import html2text
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Inicjalizacja klienta OpenAI z kluczem API z pliku .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Konfiguracja
API_KEY = os.getenv("API_KEY")
REPORT_URL = os.getenv("REPORT_URL")
QUESTIONS_URL = f"https://c3ntrala.ag3nts.org/data/{API_KEY}/softo.json"
BASE_URL = "https://softo.ag3nts.org"

def print_step(message: str):
    """Funkcja pomocnicza do wyświetlania kroków z wyróżnieniem"""
    print("\n" + "="*80)
    print(f"KROK: {message}")
    print("="*80)

class SoftoScraper:
    def __init__(self):
        self.visited_urls: List[str] = []
        self.max_depth = 3
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = True

    def get_page_content(self, url: str) -> Tuple[str, List[str]]:
        """Pobiera zawartość strony i zwraca tekst oraz listę linków."""
        print_step(f"Pobieranie zawartości strony: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Konwersja HTML do Markdown
        markdown_text = self.converter.handle(response.text)
        
        # Pobieranie linków
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = BASE_URL + href
            if href.startswith(BASE_URL):
                links.append(href)
        
        print(f"Znaleziono {len(links)} linków na stronie")
        return markdown_text, links

    def ask_llm(self, prompt: str) -> str:
        """Wysyła zapytanie do LLM i zwraca odpowiedź."""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()

    def check_for_answer(self, content: str, question: str) -> Tuple[bool, Optional[str]]:
        """Sprawdza, czy w treści znajduje się odpowiedź na pytanie."""
        print_step("Sprawdzanie czy strona zawiera odpowiedź")
        print(f"Pytanie: {question}")
        
        # Dodajemy specjalną instrukcję dla pytań o URL
        url_instruction = ""
        if "adres" in question.lower() and "https" in question.lower():
            url_instruction = "Jeśli odpowiedź jest URL-em, upewnij się że zaczyna się od 'https://'."
        
        prompt = f"""Przeanalizuj poniższą treść i odpowiedz na pytanie. Jeśli odpowiedź jest dostępna, podaj ją w maksymalnie zwięzłej formie. {url_instruction} Jeśli odpowiedź nie jest dostępna, odpowiedz 'NIE'.

Pytanie: {question}

Treść:
{content}

Odpowiedź:"""
        
        response = self.ask_llm(prompt)
        print(f"Odpowiedź LLM: {response}")
        
        if response.upper() == "NIE":
            return False, None
        return True, response

    def select_next_link(self, content: str, links: List[str], question: str) -> Optional[str]:
        """Wybiera najbardziej obiecujący link do dalszej eksploracji."""
        if not links:
            return None
            
        print_step("Wybór następnego linku do sprawdzenia")
        print(f"Dostępne linki: {json.dumps(links, indent=2)}")
        
        prompt = f"""Przeanalizuj poniższą treść i listę dostępnych linków. Wybierz jeden link, który najprawdopodobniej doprowadzi do odpowiedzi na pytanie. Odpowiedz tylko URL-em wybranego linku lub 'NIE' jeśli żaden link nie wydaje się obiecujący.

Pytanie: {question}

Treść:
{content}

Dostępne linki:
{json.dumps(links, indent=2)}

Odpowiedź:"""
        
        response = self.ask_llm(prompt)
        print(f"Wybrany link: {response}")
        
        if response.upper() == "NIE":
            return None
        return response.strip('"\'')  # Usuwamy cudzysłowy z URL-a jeśli występują

    def find_answer(self, question: str) -> Optional[str]:
        """Główna funkcja wyszukująca odpowiedź na pytanie."""
        print_step(f"Rozpoczynam wyszukiwanie odpowiedzi na pytanie: {question}")
        current_url = BASE_URL
        depth = 0
        
        while depth < self.max_depth:
            if current_url in self.visited_urls:
                print(f"URL już odwiedzony: {current_url}")
                return None
                
            self.visited_urls.append(current_url)
            content, links = self.get_page_content(current_url)
            
            # Sprawdź czy jest odpowiedź
            has_answer, answer = self.check_for_answer(content, question)
            if has_answer:
                print(f"Znaleziono odpowiedź: {answer}")
                return answer
            
            # Wybierz następny link
            next_url = self.select_next_link(content, links, question)
            if not next_url:
                print("Nie znaleziono obiecującego linku do sprawdzenia")
                return None
                
            current_url = next_url
            depth += 1
            print(f"Przechodzę do następnej strony (głębokość: {depth})")
            
        print("Osiągnięto maksymalną głębokość przeszukiwania")
        return None

def main():
    print_step("Pobieranie pytań z API")
    response = requests.get(QUESTIONS_URL)
    questions = response.json()
    print(f"Pobrane pytania: {json.dumps(questions, indent=2)}")
    
    # Inicjalizacja scrapera
    scraper = SoftoScraper()
    
    # Szukaj odpowiedzi
    answers = {}
    for q_id, question in questions.items():
        print_step(f"Przetwarzanie pytania {q_id}")
        # Resetujemy listę odwiedzonych URL-i dla każdego pytania
        scraper.visited_urls = []
        answer = scraper.find_answer(question)
        answers[q_id] = answer if answer else "Nie znaleziono odpowiedzi"
        print(f"Odpowiedź na pytanie {q_id}: {answers[q_id]}")
    
    # Przygotuj i wyślij raport
    print_step("Przygotowanie i wysyłanie raportu")
    report = {
        "task": "softo",
        "apikey": API_KEY,
        "answer": answers
    }
    print(f"Raport do wysłania: {json.dumps(report, indent=2)}")
    
    response = requests.post(REPORT_URL, json=report)
    print(f"Status odpowiedzi: {response.status_code}")
    print(f"Treść odpowiedzi: {response.text}")

if __name__ == "__main__":
    main() 