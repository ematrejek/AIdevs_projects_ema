import requests
from bs4 import BeautifulSoup
import os
import json
from PIL import Image
import whisper
import openai
from dotenv import load_dotenv
import base64
from io import BytesIO
import torch
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Załaduj zmienne środowiskowe
load_dotenv()

# Konfiguracja
API_KEY = "8eed1983-ee32-479e-8c44-eb85077a62e8"
ARTICLE_URL = "https://c3ntrala.ag3nts.org/dane/arxiv-draft.html"
QUESTIONS_URL = f"https://c3ntrala.ag3nts.org/data/{API_KEY}/arxiv.txt"

# Inicjalizacja OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Inicjalizacja modelu Whisper
whisper_model = None ## zainicjowanie zmiennej globalnej whisper_model jako None - będzie potem użyta w funkcji load_whisper_model

def load_whisper_model():
    """Ładuje model Whisper"""
    global whisper_model ## deklaracja użycia zmiennej globalnej - została stworzona poza funkcją, a chcemy się do niej odnieść oraz ją zmodyfikować
    if whisper_model is None:
        try:
            logger.info("Ładowanie modelu Whisper base") ## Zanim rozpocznie się właściwe ładowanie, funkcja zapisuje informację w logach (konsoli lub pliku, w zależności od konfiguracji logging)
            whisper_model = whisper.load_model("base") ## ładowanie modelu Whisper - w tym przypadku "base" - najmniejszy model
            logger.info("Model Whisper został pomyślnie załadowany") ## po pomyślnym załadowaniu modelu, funkcja zapisuje informację w logach
        except Exception as e:
            logger.error(f"Błąd podczas ładowania modelu Whisper: {str(e)}")
            raise
    return whisper_model



def transcribe_audio(audio_file):
    """Transkrybuje plik audio na tekst używając Whisper
    
    Args:
        audio_file (str): Ścieżka do pliku audio (MP3 lub innego obsługiwanego przez Whisper/FFmpeg)
        
    Returns:
        str: Transkrybowany tekst
    """
    try:
        
        audio_file = os.path.abspath(audio_file) ## pobranie ścieżki absolutnej do pliku audio
        
        if not os.path.exists(audio_file): ## jeżeli nie istnieje plik audio, zwróci błąd
            logger.error(f"Plik audio nie istnieje: {audio_file}")
            raise
            
        logger.info(f"Rozpoczynam transkrypcję pliku: {audio_file}")
        
        # Załaduj model jeśli nie jest załadowany
        model = load_whisper_model()
        
        # Wykonaj transkrypcję bezpośrednio na pliku
        logger.info("Wykonuję transkrypcję...")
        result = model.transcribe(str(audio_file)) ## funkcja używa FFmpeg do transkrypcji 
        ## zwróci wynik w postaci słownika zawierającego tekst oraz metadane
        
        
        logger.info("Transkrypcja zakończona pomyślnie")
        return result["text"] ## zwrócenie tekstu z wyniku transkrypcji
        
    except Exception as e:
        logger.error(f"Błąd podczas transkrypcji audio {audio_file}: {str(e)}")
        raise

def download_file(url, filename):
    """Pobiera plik z podanego URL i zapisuje go lokalnie"""
    try:
        response = requests.get(url)
        ## używa biblioteki requests do wysłania żądania HTTP typu GET na podany adres URL. Serwer powinien
        ## odpowiedzieć, przesyłająć zawartość pliku. Cała odpowiedź jest przechowywana w zmiennej "response"
        response.raise_for_status()  # sprawdza kod statusu HTTP
        ## jeżeli jest 2xx, to jest ok, nic nie robi
        ## jeżeli jest 4xx lub 5xx to rzuci wyjątek (HTTPError), pójdzie do bloku except
        
        # Upewnij się, że katalog istnieje
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        #os.path.dirname(filename) - wyciąga samą ścieżkę do katalogu z pełnej ścieżki pliku, np. z cache\plik.png robi cache
        ## os.makedirs - tworzy ten katalog, jeśli nie istnieje, exist_ok=True - jeśli istnieje, to nic nie robi
        
        with open(filename, 'wb') as f: ## otwiera plik o podanej nazwie w trybie zapisu binarnego; 'w' oznacza write, 'b' oznacza tryb binarny
            ## to jest ważne jak przetwarzamy obrazy, audio, PDF-y, żeby przetwarzać binarnie
            ## with ... as f - gwarantuje, że plik zostanie zamknięty po zakończeniu bloku with
            f.write(response.content) ## zapisuje do otwartego pliku 'f' całą zawartość pobraną z serwera (response.content zawiera surowe bajty odpowiedzi)
        logger.info(f"Pomyślnie pobrano plik: {filename}")
        return True
    except Exception as e:
        logger.error(f"Błąd podczas pobierania pliku {url}: {str(e)}")
        return False

def get_image_description(image_path):
    """Generuje opis obrazu używając OpenAI Vision API"""
    try:
        with open(image_path, "rb") as image_file: ## rb - read binary
            ## with ... as image_file - używa menadżera kontekstu, który automatycznie zamknie plik image_file po zakończeniu bloku
            response = openai.ChatCompletion.create( ## wysyła żądanie do API OpenAI używając punktu końcowego ChatCompletion, który obsługuje zadania multimodalne
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", 
                             "text": "Opisz dokładnie co widzisz na tym obrazku."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
                                    ## najpierw trzeba zakodować obrazek do postaci base64, potem decode() - przekonwertować na standardowy ciąg znaków
                                    ## ostatecznie: Oto dane (data:), są to dane typu obraz JPEG (image/jpeg;), zakodowane w Base64 (base64,), a oto one: ...".
                                }
                            } ## w tym przypadku "messages" jest listą, bo dajemy i polecenie, io brazek
                        ]
                    }
                ],
                max_tokens=150
            )
        
        return response.choices[0].message.content ## zwrócenie pierwszego trafnego wyboru, obiekt wiadomości, wyciągamy jej treść
    except Exception as e:
        logger.error(f"Błąd podczas analizy obrazu: {str(e)}")
        return "Błąd podczas analizy obrazu"

def process_html(html_content):
    """Przetwarza HTML na tekst z zachowaniem struktury"""
    soup = BeautifulSoup(html_content, 'html.parser')
    ## parsowanie HTML - parser HTML rozpoznaje słowa kluczowe (po znacznikach), ich znaczenie (np. <h1> to nagłówek)
    ## wynik parsowania to drzewo obiektów (DOM - Document Object Model)
    ## BeautifulSoup - biblioteka do parsowania HTML i XML
    ## soup - obiekt, który jest strukturą przypominającą drzewo, po której można się poruszać za pomocą metod BeautifulSoup
    
    
    for script in soup(["script", "style"]):
        script.decompose()
    ## wyszukiwanie wszystkich znaczników <script> i <style> i usuwanie ich z drzewa DOM
    ## aby pozbyć się kodu JavaScript i CSS, który nie jest potrzebny do analizy tekstu
    
    # Pobierz tekst
    text = soup.get_text()
    
    # Pobierz obrazy i ich opisy
    images = []
    for img in soup.find_all('img'):
        ## pętla poruszająca się po wszystkich znacznikach <img> w drzewie DOM
        src = img.get('src')
        ## pobranie atrybutu src, który zawiera URL obrazu
        alt = img.get('alt', '')
        ## pobranie atrybutu alt, który zawiera tekst alternatywny dla obrazu
        
        # Pobierz obraz
        if src:
            image_url = f"https://c3ntrala.ag3nts.org/dane/{src}"\
            ## jeżeli istnieje src, to pobieramy obraz z URL, zakładając, że jest to ścieżka względna
            image_path = os.path.join('cache', os.path.basename(src))
            ## tworzenie ścieżki do pliku obrazu w katalogu cache, używając os.path.basename(src) do uzyskania nazwy pliku z URL
            if download_file(image_url, image_path):
                ## wywołuje wcześniej zdefiniowanąfunkcję download_file, aby pobrać obraz z image_url i zapisać go pod image_path. Jeżeli się powiedzie, zwróci True
                # Generuj opis obrazu
                try:
                    description = get_image_description(image_path)
                    images.append({
                        'src': src,
                        'alt': alt,
                        'description': description ## to jest to, co zwraca funkcja get_image_description
                    })
                except Exception as e:
                    logger.error(f"Błąd podczas analizy obrazu {src}: {str(e)}")
                    images.append({
                        'src': src,
                        'alt': alt,
                        'description': 'Błąd podczas analizy obrazu'
                    })
    
    # Pobierz pliki audio
    audio_files = []
    audio_transcriptions = []
    
    # Szukaj wszystkich elementów audio
    audio_elements = soup.find_all('audio')
    ## znajduje wszystkie znaczniki <audio> w drzewie DOM
    logger.info(f"Znaleziono {len(audio_elements)} elementów audio na stronie")
    
    for audio in audio_elements:
        # Sprawdź atrybut src
        src = audio.get('src')
        if not src:
            # Jeśli nie ma atrybutu src, sprawdź czy jest źródło w elemencie source
            source = audio.find('source')
            if source:
                src = source.get('src')
        
        if src:
            logger.info(f"Znaleziono plik audio: {src}")
            audio_url = f"https://c3ntrala.ag3nts.org/dane/{src}"
            # Zachowaj strukturę katalogów z URL
            audio_path = os.path.join('cache', os.path.basename(src))
            ## tworzy ścieżkę do pliku audio w katalogu cache, używając os.path.basename(src) do uzyskania nazwy pliku z URL
            # Upewnij się, że katalog istnieje
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            logger.info(f"Próba pobrania pliku audio z: {audio_url}")
            if download_file(audio_url, audio_path):
                logger.info(f"Pomyślnie pobrano plik audio do: {audio_path}")
                try:
                    # Używamy audio_path do transkrypcji
                    transcription = transcribe_audio(audio_path)
                    
                    audio_files.append(os.path.basename(src))  # Zachowujemy pełną ścieżkę
                    audio_transcriptions.append({
                        'file': os.path.basename(src),  # Zachowujemy pełną ścieżkę
                        'transcription': transcription
                    })
                    logger.info(f"Pomyślnie wykonano transkrypcję pliku: {os.path.basename(src)}")
                except Exception as e:
                    logger.error(f"Błąd podczas transkrypcji audio {os.path.basename(src)}: {str(e)}")
                    audio_transcriptions.append({
                        'file': src,  # Zachowujemy pełną ścieżkę
                        'transcription': f"Błąd transkrypcji: {str(e)}"
                    })
            else:
                logger.error(f"Nie udało się pobrać pliku audio: {audio_url}")
        else:
            logger.warning("Znaleziono element audio bez źródła")
    
    return {
        'text': text,
        'images': images,
        'audio_files': audio_files,
        'audio_transcriptions': audio_transcriptions
    }

def main():
    # Utwórz katalog cache jeśli nie istnieje
    os.makedirs('cache', exist_ok=True)
    # Utwórz katalog data jeśli nie istnieje (na plik JSON)
    os.makedirs('data', exist_ok=True)
    
    # Pobierz zawartość strony
    try:
        response = requests.get(ARTICLE_URL)
        response.raise_for_status()
        html_content = response.text
        
        # Przetwórz HTML
        processed_content = process_html(html_content)
        ## wywołuje kluczową funkcję - wykonuje całą analizę; pobieranie i przetwarzanie mediów
        
        # Zapisz wyniki
        with open('data/processed_content.json', 'w', encoding='utf-8') as f:
            json.dump(processed_content, f, ensure_ascii=False, indent=2)
            
        logger.info("Przetwarzanie zakończone pomyślnie")
        
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania: {str(e)}")
        raise

if __name__ == "__main__":
    main()