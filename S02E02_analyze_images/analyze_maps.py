import os
from PIL import Image
import base64
from io import BytesIO
import requests
import json
from typing import Dict
import logging
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe z pliku .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MapAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Brak klucza API OpenAI w pliku .env")
            
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        logger.info("Inicjalizacja analizatora map z GPT-4o")

    def encode_image(self, image_path: str) -> str:
        """Koduje obraz do formatu base64."""
        with Image.open(image_path) as image:
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze_image(self, image_path: str) -> str:
        """Analizuje pojedynczy obraz mapy używając GPT-4o."""
        try:
            base64_image = self.encode_image(image_path)
            
            prompt = """Przeanalizuj dokładnie ten fragment mapy miasta. Zwróć szczególną uwagę na:
            1. Nazwy ulic - przeczytaj dokładnie wszystkie widoczne nazwy
            2. Charakterystyczne budynki i obiekty (kościoły, szkoły, cmentarze, parki)
            3. Układ urbanistyczny (regularny/nieregularny, typ zabudowy)
            4. Wszelkie inne charakterystyczne elementy, które mogą pomóc zidentyfikować miasto
            
            Odpowiedz w formacie:
            ULICY: [lista wszystkich widocznych nazw ulic]
            OBIEKTY: [lista wszystkich widocznych obiektów]
            UKŁAD: [dokładny opis układu urbanistycznego]
            MIASTO: [nazwa miasta, jeśli jesteś pewien, lub "niepewne" jeśli nie możesz określić]"""

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }

            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    logger.error("Model GPT-4o nie jest dostępny. Sprawdź, czy masz dostęp do tego modelu w swoim koncie OpenAI.")
                elif e.response.status_code == 401:
                    logger.error("Nieprawidłowy klucz API. Sprawdź swój klucz API w pliku .env")
                else:
                    logger.error(f"Błąd HTTP: {str(e)}")
                return ""
            except json.JSONDecodeError:
                logger.error("Nieprawidłowa odpowiedź z API")
                return ""
            
        except Exception as e:
            logger.error(f"Błąd podczas analizy obrazu {image_path}: {str(e)}")
            return ""

    def analyze_all_maps(self, map_dir: str) -> Dict[str, str]:
        """Analizuje wszystkie fragmenty map w podanym katalogu."""
        results = {}
        for filename in os.listdir(map_dir):
            if filename.endswith(('.jpg', '.JPG', '.png', '.PNG')):
                image_path = os.path.join(map_dir, filename)
                logger.info(f"Analizuję {filename}")
                results[filename] = self.analyze_image(image_path)
        return results

def main():
    try:
        analyzer = MapAnalyzer()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        results = analyzer.analyze_all_maps(current_dir)
        
        print("\nWyniki analizy map:")
        print("=" * 50)
        for filename, analysis in results.items():
            print(f"\nAnaliza {filename}:")
            print(analysis)
            print("-" * 50)
    except Exception as e:
        logger.error(f"Wystąpił błąd: {str(e)}")

if __name__ == "__main__":
    main() 