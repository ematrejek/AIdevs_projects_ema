from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import re
import logging
from typing import Optional
import time
import os
from datetime import datetime

# Konfiguracja logowania
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"dron_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # Dodatkowo wyświetla logi w konsoli
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Rozpoczęto logowanie do pliku: {log_file}")
print(f"\nLogi są zapisywane do pliku: {log_file}\n")  # Wyświetl ścieżkę w konsoli

app = FastAPI()

MAPA = [
    ["start", "trawa", "drzewo", "dom"],
    ["trawa", "wiatrak", "trawa", "trawa"],
    ["trawa", "trawa", "skały", "dwa drzewa"],
    ["góry", "góry", "samochód", "jaskinia"]
]

LICZEBNIKI = {
    "jeden": 1, "jedno": 1, "pierwsze": 1, "pierwszy": 1, "pierwsza": 1,
    "dwa": 2, "dwie": 2, "drugie": 2, "drugi": 2, "druga": 2,
    "trzy": 3, "trzecie": 3, "trzeci": 3, "trzecia": 3,
    "cztery": 4, "czwarte": 4, "czwarty": 4, "czwarta": 4,
    "pięć": 5, "piąte": 5, "piąty": 5, "piąta": 5,
    "sześć": 6, "szóste": 6, "szósty": 6, "szósta": 6,
    "siedem": 7, "siódme": 7, "siódmy": 7, "siódma": 7,
    "osiem": 8, "ósme": 8, "ósmy": 8, "ósma": 8,
    "dziewięć": 9, "dziewiąte": 9, "dziewiąty": 9, "dziewiąta": 9,
    "dziesięć": 10, "dziesiąte": 10, "dziesiąty": 10, "dziesiąta": 10
}

# For regex construction
numerals_regex_part = "|".join(LICZEBNIKI.keys())
number_capture_regex = r"(\d+|" + numerals_regex_part + r")"
units_regex_part = r"(?: pola| pól| kroki| kroków| krok| kratki| kratek| pole| kratkę| pól)?"
preposition_regex_part = r"(?: ?(?:w |we |na |do |po |przez ))?"
direction_regex_group = r"(prawo|lewo|dół|dolu|górę|gora|gore|gory|w prawo|w lewo|w dół|w górę|w prawej|w lewej|w dolnej|w górnej)"

DIRECTION_EFFECTS = {
    "prawo": (1, 0), "w prawo": (1, 0), "w prawej": (1, 0),
    "lewo": (-1, 0), "w lewo": (-1, 0), "w lewej": (-1, 0),
    "dół": (0, 1), "dolu": (0, 1), "w dół": (0, 1), "w dolnej": (0, 1),
    "góra": (0, -1), "górę": (0, -1), "gora": (0, -1), "gore": (0, -1), "gory": (0, -1), "w górę": (0, -1), "w górnej": (0, -1)
}

class InstrukcjaDrona(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=1000)

def get_dx_dy_for_direction_str(dir_str: str) -> tuple[int, int] | None:
    dir_str_lower = dir_str.lower()
    return DIRECTION_EFFECTS.get(dir_str_lower)

def wykonaj_ruch(x: int, y: int, fraza_lower_stripped: str) -> tuple[int, int]:
    start_time = time.time()
    logger.info(f"Przetwarzanie instrukcji: '{fraza_lower_stripped}' z pozycji ({x}, {y})")
    
    # Ignoruj frazy, które nie są instrukcjami ruchu
    if any(słowo in fraza_lower_stripped for słowo in ["słuchaj", "widzisz", "co tam", "kolego"]):
        logger.info(f"Pominięto frazę bez instrukcji ruchu: '{fraza_lower_stripped}'")
        return x, y
    
    # --- 1. Absolute Edge Movements ---
    # Down
    if re.search(r"na sam dół|do samego dołu|(?:na )?dół do końca|maksymalnie w dół|w dół maksymalnie|ile tylko możemy (?:polecieć |iść )?w dół|w dół ile tylko możemy|do oporu w dół|w dół do oporu|na dolną krawędź|do dolnej krawędzi|ile wlezie w dół", fraza_lower_stripped):
        logger.info("Wykryto ruch do dolnej krawędzi")
        y = 3
        logger.info(f"Nowa pozycja: ({x}, {y})")
        return x, y
    # Right
    if re.search(r"na sam prawo|do końca w prawo|w prawo do końca|maksymalnie w prawo|w prawo maksymalnie|ile tylko możemy (?:polecieć |iść )?w prawo|w prawo ile tylko możemy|do oporu w prawo|w prawo do oporu|na prawą krawędź|do prawej krawędzi|na maksa w prawo", fraza_lower_stripped):
        logger.info("Wykryto ruch do prawej krawędzi")
        x = 3
        logger.info(f"Nowa pozycja: ({x}, {y})")
        return x, y
    # Left
    if re.search(r"na sam lewo|do końca w lewo|w lewo do końca|maksymalnie w lewo|w lewo maksymalnie|ile tylko możemy (?:polecieć |iść )?w lewo|w lewo ile tylko możemy|do oporu w lewo|w lewo do oporu|na lewą krawędź|do lewej krawędzi", fraza_lower_stripped):
        logger.info("Wykryto ruch do lewej krawędzi")
        x = 0
        logger.info(f"Nowa pozycja: ({x}, {y})")
        return x, y
    # Up
    if re.search(r"na samą górę|do końca w górę|w górę do końca|maksymalnie w górę|w górę maksymalnie|ile tylko możemy (?:polecieć |iść )?w górę|w górę ile tylko możemy|do oporu w górę|w górę do oporu|na górną krawędź|do górnej krawędzi", fraza_lower_stripped):
        logger.info("Wykryto ruch do górnej krawędzi")
        y = 0
        logger.info(f"Nowa pozycja: ({x}, {y})")
        return x, y

    # --- 2. Relative Movements ---
    liczba_val = 1 # Default
    dx_val, dy_val = 0, 0
    move_parsed = False

    # Pattern 1: Number ... Direction
    regex_n_dir = fr"{number_capture_regex}?{units_regex_part}{preposition_regex_part} ?{direction_regex_group}"
    match_n_dir = re.search(regex_n_dir, fraza_lower_stripped)
    if match_n_dir:
        num_str = match_n_dir.group(1) # Optional number part
        dir_str = match_n_dir.group(2) # Direction part

        if num_str:
            if num_str.isdigit(): 
                liczba_val = int(num_str)
                logger.info(f"Wykryto liczbę cyfrową: {liczba_val}")
            elif num_str.lower() in LICZEBNIKI: 
                liczba_val = LICZEBNIKI[num_str.lower()]
                logger.info(f"Wykryto liczbę słowną: {liczba_val}")
        
        effects = get_dx_dy_for_direction_str(dir_str)
        if effects:
            dx_val, dy_val = effects
            logger.info(f"Wykryto kierunek: {dir_str} (dx={dx_val}, dy={dy_val})")
            move_parsed = True

    if not move_parsed:
        # Pattern 2: Direction ... Number
        regex_dir_n = fr"{direction_regex_group}{preposition_regex_part} ?{number_capture_regex}?{units_regex_part}"
        match_dir_n = re.search(regex_dir_n, fraza_lower_stripped)
        if match_dir_n:
            dir_str = match_dir_n.group(1) # Direction part
            num_str = match_dir_n.group(2) # Optional number part

            if num_str:
                if num_str.isdigit(): 
                    liczba_val = int(num_str)
                    logger.info(f"Wykryto liczbę cyfrową: {liczba_val}")
                elif num_str.lower() in LICZEBNIKI: 
                    liczba_val = LICZEBNIKI[num_str.lower()]
                    logger.info(f"Wykryto liczbę słowną: {liczba_val}")

            effects = get_dx_dy_for_direction_str(dir_str)
            if effects:
                dx_val, dy_val = effects
                logger.info(f"Wykryto kierunek: {dir_str} (dx={dx_val}, dy={dy_val})")
                move_parsed = True
    
    if move_parsed:
        old_x, old_y = x, y
        x += dx_val * liczba_val
        y += dy_val * liczba_val
        logger.info(f"Wykonano ruch: ({old_x}, {old_y}) -> ({x}, {y})")
    else:
        logger.info(f"Nie wykryto ruchu w instrukcji: {fraza_lower_stripped}")

    # Clamp coordinates
    old_x, old_y = x, y
    x = max(0, min(3, x))
    y = max(0, min(3, y))
    if old_x != x or old_y != y:
        logger.info(f"Pozycja została ograniczona do granic mapy: ({old_x}, {old_y}) -> ({x}, {y})")
    
    # Sprawdź timeout
    execution_time = time.time() - start_time
    if execution_time > 0.1:  # 100ms timeout
        logger.warning(f"Timeout podczas przetwarzania instrukcji: {fraza_lower_stripped} (czas: {execution_time:.3f}s)")
    else:
        logger.debug(f"Czas wykonania: {execution_time:.3f}s")
        
    return x, y

def interpretuj_instrukcje(instrukcja: str) -> str:
    try:
        logger.info(f"Rozpoczynam interpretację instrukcji: '{instrukcja}'")
        current_x, current_y = 0, 0
        logger.info(f"Pozycja początkowa: ({current_x}, {current_y})")

        raw_phrases = re.split(r",| a potem | a następnie | następnie | i oraz | i potem | i następnie | i | oraz | potem | później |\.|;|!|\n", instrukcja.lower())
        logger.info(f"Podzielono na {len(raw_phrases)} fraz")
        
        phrases_to_process = []
        for fraza_raw in raw_phrases:
            f_strip_lower = fraza_raw.strip()
            if not f_strip_lower:
                continue
            
            if "zaczynamy od nowa" in f_strip_lower or f_strip_lower == "od nowa":
                logger.info("Wykryto komendę resetu pozycji")
                phrases_to_process = [] 
                current_x, current_y = 0, 0
                continue 
            phrases_to_process.append(f_strip_lower)
            logger.debug(f"Dodano frazę do przetworzenia: '{f_strip_lower}'")

        for i, phrase in enumerate(phrases_to_process, 1):
            logger.info(f"Przetwarzanie frazy {i}/{len(phrases_to_process)}: '{phrase}'")
            current_x, current_y = wykonaj_ruch(current_x, current_y, phrase)
            logger.info(f"Pozycja po frazie {i}: ({current_x}, {current_y})")
                
        final_x = max(0, min(3, current_x))
        final_y = max(0, min(3, current_y))
        
        if final_x != current_x or final_y != current_y:
            logger.info(f"Pozycja końcowa została ograniczona: ({current_x}, {current_y}) -> ({final_x}, {final_y})")
        
        opis = MAPA[final_y][final_x]
        logger.info(f"Znaleziono opis na pozycji ({final_x}, {final_y}): '{opis}'")
        return opis
    except Exception as e:
        logger.error(f"Błąd podczas interpretacji instrukcji: {str(e)}", exc_info=True)
        return "błąd"

@app.post("/dron", status_code=200)
async def endpoint_drona(data: InstrukcjaDrona):
    try:
        logger.info(f"Otrzymano nowe żądanie z instrukcją: '{data.instruction}'")
        
        if not data.instruction or data.instruction.strip() == "":
            logger.info("Pusta instrukcja - zwracam opis punktu startowego")
            opis = MAPA[0][0]
        else:
            opis = interpretuj_instrukcje(data.instruction)
            
        logger.info(f"Zwracam odpowiedź: '{opis}'")
        return {"description": opis}
    except Exception as e:
        logger.error(f"Błąd w endpoincie: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Wystąpił błąd podczas przetwarzania instrukcji")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)