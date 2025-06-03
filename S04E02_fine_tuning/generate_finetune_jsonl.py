import json

# Ścieżki do plików
correct_path = 'correct.txt'
incorrect_path = 'incorect.txt'
out_path = 'finetune_data.jsonl'

# Funkcja do generowania rekordu JSONL
def make_record(line, label):
    return {
        "messages": [
            {"role": "system", "content": "validate data"},
            {"role": "user", "content": line.strip()},
            {"role": "assistant", "content": label}
        ]
    }

def main():
    with open(out_path, 'w', encoding='utf-8') as fout:
        # Dane poprawne
        with open(correct_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    rec = make_record(line, "1")
                    fout.write(json.dumps(rec, ensure_ascii=False) + '\n')
        # Dane niepoprawne
        with open(incorrect_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    rec = make_record(line, "0")
                    fout.write(json.dumps(rec, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    main() 