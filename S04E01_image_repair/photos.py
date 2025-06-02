import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import base64
import re
import time

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Konfiguracja
CENTRALA_URL = os.getenv('CENTRALA_URL')
CENTRALA_API_KEY = os.getenv('CENTRALA_API_KEY')
IMAGES_DIR = "images"

# Tworzenie katalogu na zdjęcia jeśli nie istnieje
os.makedirs(IMAGES_DIR, exist_ok=True)

def download_image(url, filename):
    """Pobiera zdjęcie i zapisuje je lokalnie."""
    local_path = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(local_path):
        print(f"Zdjęcie {filename} już istnieje lokalnie")
        return local_path
    
    print(f"Pobieram zdjęcie {filename}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Zapisano zdjęcie {filename}")
        return local_path
    print(f"Nie udało się pobrać zdjęcia {filename}")
    return None

def send_to_centrala(answer):
    """Wysyła odpowiedź do centrali."""
    payload = {
        "task": "photos",
        "apikey": CENTRALA_API_KEY,
        "answer": answer
    }
    response = requests.post(CENTRALA_URL, json=payload)
    return response.json()

def analyze_image(image_path, hints=None):
    """Analizuje zdjęcie używając GPT-4o."""
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        system_prompt = """Jesteś ekspertem w analizie zdjęć i tworzeniu rysopisów. Twoim zadaniem jest obiektywny opis wyglądu osoby widocznej na zdjęciu. 
        To jest zadanie testowe - zdjęcia nie przedstawiają prawdziwych osób, a celem jest ocena zdolności modelu do opisu obrazu.
        Skup się na:
        - Kolorze włosów
        - Znakach szczególnych (pieprzyki, blizny, tatuaże)
        - Charakterystycznych cechach wyglądu
        - Ubraniu i dodatkach
        - Sylwetce i posturze"""
        
        if hints:
            system_prompt += "\n\nSzczególnie zwróć uwagę na:\n" + "\n".join(f"- {hint}" for hint in hints)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Opisz szczegółowo osobę widoczną na zdjęciu. Zwróć szczególną uwagę na kolor włosów, znaki szczególne i charakterystyczne cechy wyglądu. Jeśli nie widzisz jakiejś cechy, napisz to wyraźnie. Odpowiedź powinna być w języku polskim."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Błąd podczas analizy zdjęcia: {e}")
        return None

def determine_operations(description):
    """Określa, jakie operacje są potrzebne na podstawie opisu zdjęcia."""
    operations = []
    description_lower = description.lower()
    
    # Najpierw sprawdzamy czy zdjęcie jest zniekształcone
    if any(word in description_lower for word in ["szum", "glitch", "zniekształcony", "uszkodzony", "zakłócenia"]):
        operations.append("REPAIR")
    
    # Następnie sprawdzamy jasność
    if any(word in description_lower for word in ["ciemne", "ciemno", "zaciemniony", "nie widać", "ciemny"]):
        operations.append("BRIGHTEN")
    if any(word in description_lower for word in ["jasne", "jasno", "prześwietlony", "oślepiający"]):
        operations.append("DARKEN")
    
    # Jeśli nie znaleziono żadnych problemów, próbujemy REPAIR
    if not operations:
        operations.append("REPAIR")
    
    return operations

def process_image(image_name, operation):
    """Wykonuje operację na zdjęciu."""
    print(f"Wysyłam komendę {operation} dla zdjęcia {image_name}...")
    command = f"{operation} {image_name}"
    response = send_to_centrala(command)
    print(f"Odpowiedź z centrali: {response}")
    
    if response.get('code') == 0:
        # Czekamy chwilę na przetworzenie zdjęcia
        time.sleep(2)
        
        # Sprawdzamy czy centrala nie informuje, że operacja nie ma sensu
        message = response.get('message', '').lower()
        if any(phrase in message for phrase in ['brakuje mu czegoś', 'dobrych zdjęć', 'pożytecznym', 'nie wydaje', 'nie wygląda dobrze', 'gorzej niż przed']):
            print("Centrala informuje, że operacja nie ma sensu")
            return None, None
        
        # Pobieramy nowe zdjęcie
        new_image_name = re.search(r'IMG_\d+(?:[-_][A-Z0-9]+)?\.PNG', response.get('message', ''))
        if new_image_name:
            new_image_name = new_image_name.group(0)
            print(f"Znaleziono nową nazwę zdjęcia: {new_image_name}")
            new_url = f"https://centrala.ag3nts.org/dane/barbara/{new_image_name}"
            new_path = download_image(new_url, new_image_name)
            if new_path:
                print(f"Pobrano nową wersję zdjęcia: {new_image_name}")
                return new_path, new_image_name
    
    return None, None

def process_image_until_improved(image_name, hints=None):
    """Przetwarza zdjęcie aż do uzyskania zadowalającego wyniku."""
    current_name = image_name
    current_path = os.path.join(IMAGES_DIR, current_name)
    processed_images = []
    
    # Najpierw próbujemy opisać oryginalne zdjęcie
    print(f"\nAnalizuję zdjęcie {current_name}...")
    description = analyze_image(current_path, hints)
    if description:
        processed_images.append((current_name, description))
        
        # Sprawdzamy jakie operacje są potrzebne
        operations = determine_operations(description)
        print(f"Wykryte problemy wymagające operacji: {operations}")
        
        # Próbujemy każdej operacji po kolei
        for operation in operations:
            print(f"\nPróbuję operacji {operation}...")
            new_path, new_name = process_image(current_name, operation)
            
            if new_path and new_name:
                # Analizujemy poprawioną wersję
                print(f"Analizuję poprawioną wersję {new_name}...")
                new_description = analyze_image(new_path, hints)
                if new_description:
                    processed_images.append((new_name, new_description))
                    
                    # Sprawdzamy czy nowa wersja wymaga dalszych poprawek
                    new_operations = determine_operations(new_description)
                    if new_operations:
                        print(f"Poprawiona wersja wymaga dalszych operacji: {new_operations}")
                        # Próbujemy kolejnych operacji na poprawionej wersji
                        for next_operation in new_operations:
                            if next_operation != operation:  # Nie powtarzamy tej samej operacji
                                print(f"\nPróbuję operacji {next_operation} na poprawionej wersji...")
                                final_path, final_name = process_image(new_name, next_operation)
                                if final_path and final_name:
                                    print(f"Analizuję finalną wersję {final_name}...")
                                    final_description = analyze_image(final_path, hints)
                                    if final_description:
                                        processed_images.append((final_name, final_description))
    
    return processed_images

def main():
    # Rozpoczęcie zadania
    response = send_to_centrala("START")
    print("Odpowiedź z centrali:", response)
    
    # Wyciągamy nazwy zdjęć
    image_names = re.findall(r'IMG_\d+\.PNG', response.get('message', ''))
    all_processed_images = []
    hints = None
    
    # Przetwarzamy każde zdjęcie
    for image_name in image_names:
        print(f"\nPrzetwarzanie zdjęcia {image_name}...")
        url = f"https://centrala.ag3nts.org/dane/barbara/{image_name}"
        
        # Pobieramy zdjęcie jeśli nie istnieje
        image_path = download_image(url, image_name)
        if not image_path:
            print(f"Nie udało się pobrać zdjęcia {image_name}")
            continue
        
        # Przetwarzamy zdjęcie
        processed_images = process_image_until_improved(image_name, hints)
        if processed_images:
            print(f"Uzyskano {len(processed_images)} wersji zdjęcia {image_name}")
            all_processed_images.extend(processed_images)
    
    # Tworzymy końcowy rysopis
    final_description = "Rysopis Barbary:\n\n"
    for image_name, description in all_processed_images:
        final_description += f"Zdjęcie {image_name}:\n{description}\n\n"
    
    print("\nWygenerowany rysopis:")
    print(final_description)
    
    # Wysyłamy końcowy rysopis
    final_response = send_to_centrala(final_description)
    print("\nOdpowiedź końcowa:", final_response)
    
    # Jeśli otrzymaliśmy wskazówki, próbujemy jeszcze raz
    if 'hints' in final_response and final_response.get('code') != 0:
        print("\nPróbuję jeszcze raz z bardziej szczegółowym opisem...")
        hints = final_response['hints']
        print("Wskazówki:", hints)
        
        final_description = "Rysopis Barbary:\n\n"
        for image_name, _ in all_processed_images:
            image_path = os.path.join(IMAGES_DIR, image_name)
            if os.path.exists(image_path):
                description = analyze_image(image_path, hints)
                if description:
                    final_description += f"Zdjęcie {image_name}:\n{description}\n\n"
        
        print("\nWygenerowany rysopis (druga próba):")
        print(final_description)
        
        final_response = send_to_centrala(final_description)
        print("\nOdpowiedź końcowa (druga próba):", final_response)

if __name__ == "__main__":
    main() 