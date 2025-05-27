import os
from openai import OpenAI
import json
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pl"
        )
    return transcript.text

def main():
    # Katalog z plikami audio
    audio_dir = "."
    
    # Słownik do przechowywania transkrypcji
    transcripts = {}
    
    # Przetwarzanie każdego pliku audio
    for filename in os.listdir(audio_dir):
        if filename.endswith(".m4a"):
            print(f"Transkrybuję {filename}...")
            file_path = os.path.join(audio_dir, filename)
            transcript = transcribe_audio(file_path)
            transcripts[filename] = transcript
    
    # Zapisz transkrypcje do pliku JSON
    with open("transcripts.json", "w", encoding="utf-8") as f:
        json.dump(transcripts, f, ensure_ascii=False, indent=2)
    
    print("Transkrypcje zostały zapisane do pliku transcripts.json")

if __name__ == "__main__":
    main() 