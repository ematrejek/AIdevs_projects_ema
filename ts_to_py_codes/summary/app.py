import asyncio
import os
import re
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json # Chociaż nie jest bezpośrednio używany w promptach, może być przydatny

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Inicjalizacja klienta OpenAI
# Upewnij się, że masz ustawioną zmienną środowiskową OPENAI_API_KEY
# lub przekaż klucz API bezpośrednio: client = AsyncOpenAI(api_key="TWÓJ_KLUCZ_API")
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Pobranie ścieżki do bieżącego katalogu skryptu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_result(content: str, tag_name: str) -> str | None:
    """
    Wyciąga zawartość spomiędzy tagów w stylu XML.

    Args:
        content: Ciąg znaków zawierający tagi w stylu XML.
        tag_name: Nazwa tagu, z którego ma być wyciągnięta zawartość.

    Returns:
        Zawartość wewnątrz określonych tagów lub None, jeśli nie znaleziono.
    """
    regex = re.compile(f"<{tag_name}>(.*?)</{tag_name}>", re.DOTALL) # re.DOTALL pozwala '.' dopasować nową linię
    match = regex.search(content)
    return match.group(1).strip() if match else None

async def extract_information(title: str, text: str, extraction_type: str, description: str, model: str = "gpt-4") -> str:
    """
    Wyciąga informacje określonego typu z podanego tekstu.

    Args:
        title: Tytuł artykułu.
        text: Tekst wejściowy, z którego mają być wyciągnięte informacje.
        extraction_type: Typ informacji do wyciągnięcia.
        description: Opis typu ekstrakcji.
        model: Model OpenAI do użycia.

    Returns:
        Ciąg znaków zawierający wyciągnięte informacje.
    """
    extraction_message = {
        "role": "system",
        "content": f"""Jesteś ekspertem w precyzyjnej ekstrakcji informacji. Twoim zadaniem jest wyciągnąć "{extraction_type}" ({description}) z wiadomości użytkownika w kontekście artykułu o tytule "{title}".
Przekształć treść w jasne, ustrukturyzowane, ale proste punkty. Nie używaj formatowania, z wyjątkiem linków i obrazów, jeśli są obecne w oryginalnej wiadomości.

Formatuj linki i obrazy w następujący sposób (jeśli występują):
- nazwa_linku_lub_obrazu: krótki opis z linkiem/obrazem.

Zachowaj pełną dokładność oryginalnej wiadomości. Odpowiedz tylko wyekstrahowaną treścią, bez dodatkowych komentarzy.
Jeśli nie znajdziesz informacji danego typu, odpowiedz: "Nie znaleziono {extraction_type}."
"""
    }

    user_message = {
        "role": "user",
        "content": f"Oto artykuł, z którego musisz wyciągnąć informacje:\n\n---\n{text}\n---"
    }

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[extraction_message, user_message]
        )
        return response.choices[0].message.content or f"Nie udało się wyekstrahować {extraction_type}."
    except Exception as e:
        print(f"Błąd podczas ekstrakcji '{extraction_type}': {e}")
        return f"Błąd podczas ekstrakcji {extraction_type}."

async def draft_summary(title: str, article: str, context: str, entities: str, links: str, topics: str, takeaways: str, model: str = "gpt-4") -> str:
    """
    Tworzy wersję roboczą szczegółowego artykułu na podstawie oryginalnego tekstu i wyekstrahowanych kontekstów.
    """
    draft_message_content = f"""Jako copywriter, stwórz samodzielny, w pełni szczegółowy artykuł na podstawie "{title}", który można zrozumieć bez czytania oryginału. Pisz w formacie markdown, włączając wszystkie obrazy w treść. Artykuł musi:

Pisz po polsku, upewniając się, że każdy kluczowy element z oryginału jest zawarty, jednocześnie:
- Bądź zmotywowany i dokładny, upewniając się, że nigdy nie pominiesz szczegółów potrzebnych do zrozumienia artykułu.
- NIGDY nie odwołuj się do oryginalnego artykułu.
- Zawsze zachowuj oryginalne nagłówki i podnagłówki.
- Naśladuj styl pisania, ton, wyrażenia i głos oryginalnego autora.
- Prezentuj WSZYSTKIE główne punkty z pełnym kontekstem i wyjaśnieniem.
- Podążaj za oryginalną strukturą i przepływem, nie pomijając żadnych szczegółów.
- Włącz każdy temat, podtemat i spostrzeżenie w sposób kompleksowy.
- Zachowaj cechy pisarskie i perspektywę autora.
- Upewnij się, że czytelnicy mogą w pełni zrozumieć temat bez wcześniejszej wiedzy.
- Użyj tytułu: "{title}" jako tytułu artykułu, który tworzysz. Podążaj za wszystkimi innymi nagłówkami i podnagłówkami z oryginalnego artykułu.
- Dołącz obraz okładki, jeśli jest dostępny w oryginalnym artykule lub kontekstach.

Przed pisaniem, przeanalizuj oryginał, aby uchwycić:
* Elementy stylu pisania
* Wszystkie obrazy, linki i filmy Vimeo z oryginalnego artykułu (jeśli dostarczone w kontekstach)
* Uwzględnij przykłady, cytaty i kluczowe punkty z oryginalnego artykułu (jeśli dostarczone w kontekstach)
* Wzorce językowe i ton
* Podejścia retoryczne
* Metody prezentacji argumentów

Uwaga: Zabrania się używania języka o wysokim ładunku emocjonalnym, takiego jak "rewolucyjny", "innowacyjny", "potężny", "niesamowity", "przełomowy", "zanurz się", "zagłęb się" itp.

Odwołaj się i zintegruj WSZYSTKIE poniższe elementy w formacie markdown:

<context>
{context}
</context>
<entities>
{entities}
</entities>
<links>
{links}
</links>
<topics>
{topics}
</topics>
<key_insights>
{takeaways}
</key_insights>

<original_article>
{article}
</original_article>

Stwórz nowy artykuł wewnątrz tagów <final_answer>. Ostateczny tekst musi stanowić samodzielne, kompletne dzieło, zawierające wszystkie niezbędne informacje, kontekst i wyjaśnienia z oryginalnego artykułu. Żaden szczegół nie powinien pozostać niewyjaśniony ani zakładany jako wcześniejsza wiedza.
"""
    draft_message = {
        "role": "user", # W oryginalnym kodzie TS jest 'user', co ma sens, bo to główna instrukcja
        "content": draft_message_content
    }
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[draft_message]
        )
        return response.choices[0].message.content or "Nie udało się stworzyć wersji roboczej."
    except Exception as e:
        print(f"Błąd podczas tworzenia wersji roboczej: {e}")
        return "Błąd podczas tworzenia wersji roboczej."


async def critique_summary(summary_draft: str, article: str, context: str, model: str = "gpt-4") -> str:
    """
    Krytycznie analizuje dostarczoną wersję roboczą podsumowania.
    """
    critique_message_content = f"""Przeanalizuj dostarczoną skompresowaną wersję artykułu krytycznie, skupiając się wyłącznie na jej dokładności faktycznej, strukturze i kompleksowości w odniesieniu do danego kontekstu.

<analysis_parameters>
GŁÓWNY CEL: Porównaj skompresowaną wersję z oryginalną treścią z wymogiem 100% precyzji.

PROTOKÓŁ WERYFIKACJI:
- Każde stwierdzenie musi dokładnie odpowiadać materiałowi źródłowemu.
- Każda koncepcja wymaga bezpośredniej walidacji źródłowej.
- Niedozwolone są żadne interpretacje ani założenia.
- Formatowanie markdown musi być dokładnie zachowane.
- Wszystkie informacje techniczne muszą zachować pełną dokładność.

KRYTYCZNE PUNKTY OCENY:
1. Weryfikacja na poziomie stwierdzeń w odniesieniu do źródła.
2. Ocena dokładności technicznej.
3. Sprawdzenie zgodności formatowania.
4. Walidacja linków i odniesień.
5. Weryfikacja umiejscowienia obrazów.
6. Sprawdzenie kompletności koncepcyjnej.

<original_article>
{article}
</original_article>

<context desc="To może pomóc Ci lepiej zrozumieć artykuł.">
{context}
</context>

<compressed_version>
{summary_draft}
</compressed_version>

WYMAGANIA DOTYCZĄCE ODPOWIEDZI:
- Zidentyfikuj WSZYSTKIE odchylenia, niezależnie od skali.
- Zgłoś dokładną lokalizację każdej rozbieżności.
- Podaj konkretne wymagania dotyczące korekty.
- Precyzyjnie dokumentuj brakujące elementy.
- Zaznacz wszelkie nieautoryzowane dodatki.

Twoje zadanie: Przeprowadź kompleksową analizę skompresowanej wersji w odniesieniu do materiału źródłowego. Zdokumentuj każde odchylenie. Bez wyjątków. Odpowiedz tylko treścią krytyki.
"""
    critique_message = {
        "role": "system", # W oryginalnym kodzie TS jest 'system', co ma sens dla instrukcji analitycznych
        "content": critique_message_content
    }
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[critique_message]
        )
        return response.choices[0].message.content or "Nie udało się wygenerować krytyki."
    except Exception as e:
        print(f"Błąd podczas generowania krytyki: {e}")
        return "Błąd podczas generowania krytyki."

async def create_final_summary(refined_draft_content: str, topics: str, takeaways: str, critique: str, context: str, model: str = "gpt-4") -> str:
    """
    Tworzy finalną, skompresowaną wersję artykułu, uwzględniając krytykę.
    """
    summarize_message_content = f"""Stwórz ostateczną skompresowaną wersję artykułu, która zaczyna się od wstępnego zwięzłego przeglądu, następnie omawia wszystkie kluczowe tematy, wykorzystując dostępną wiedzę w skondensowany sposób, i kończy się istotnymi spostrzeżeniami oraz uwagami końcowymi.
Rozważ dostarczoną krytykę i odnieś się do wszelkich problemów, które porusza.

Ważne: Uwzględnij odpowiednie linki i obrazy z kontekstu w formacie markdown. NIE dołączaj żadnych linków ani obrazów, które nie są jawnie wymienione w kontekście.
Uwaga: Zabrania się używania języka o wysokim ładunku emocjonalnym, takiego jak "rewolucyjny", "innowacyjny", "potężny", "niesamowity", "przełomowy", "zanurz się", "zagłęb się" itp.

Wymaganie: Użyj języka polskiego.

Wytyczne dotyczące kompresji:
- Zachowaj główny przekaz i kluczowe punkty oryginalnego artykułu.
- Zawsze zachowuj oryginalne nagłówki i podnagłówki.
- Upewnij się, że obrazy, linki i filmy są obecne w Twojej odpowiedzi, jeśli są w dostarczonych kontekstach.
- Wyeliminuj redundancje i nieistotne szczegóły.
- Używaj zwięzłego języka i struktur zdaniowych.
- Zachowaj oryginalny ton i styl artykułu w skondensowanej formie.

Dostarcz ostateczną skompresowaną wersję wewnątrz tagów <final_answer>.

<refined_draft>
{refined_draft_content}
</refined_draft>
<topics>
{topics}
</topics>
<key_insights>
{takeaways}
</key_insights>
<critique note="To jest ważne, ponieważ zostało stworzone na podstawie wstępnej wersji roboczej skompresowanej wersji. Rozważ to, zanim zaczniesz pisać ostateczną skompresowaną wersję.">
{critique}
</critique>
<context>
{context}
</context>

Zacznijmy.
"""
    summarize_message = {
        "role": "user", # W oryginalnym kodzie TS jest 'user'
        "content": summarize_message_content
    }
    try:
        response = await client.chat.completions.create(
            model=model, # W TS było 'o1-preview', tutaj używamy przekazanego modelu
            messages=[summarize_message]
        )
        return response.choices[0].message.content or "Nie udało się stworzyć finalnego podsumowania."
    except Exception as e:
        print(f"Błąd podczas tworzenia finalnego podsumowania: {e}")
        return "Błąd podczas tworzenia finalnego podsumowania."

async def generate_detailed_summary():
    """
    Orkiestruje wszystkimi krokami przetwarzania, aby wygenerować szczegółowe podsumowanie.
    """
    article_path = os.path.join(BASE_DIR, 'article.md')
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            article = f.read()
    except FileNotFoundError:
        print(f"Błąd: Plik '{article_path}' nie został znaleziony.")
        print("Proszę utworzyć plik 'article.md' w tym samym katalogu co skrypt i umieścić w nim treść artykułu.")
        return
    except Exception as e:
        print(f"Błąd podczas odczytu pliku article.md: {e}")
        return

    title = 'AI_devs 3, Lekcja 1, Moduł 1 — Interakcja z dużym modelem językowym' # Można to uczynić dynamicznym

    extraction_types = [
        {'key': 'topics', 'description': 'Główne tematy poruszone w artykule. Skup się tutaj na nagłówkach i wszystkich konkretnych tematach omówionych w artykule.'},
        {'key': 'entities', 'description': 'Wymienione osoby, miejsca lub rzeczy wspomniane w artykule. Pomiń linki i obrazy.'},
        {'key': 'keywords', 'description': 'Kluczowe terminy i frazy z treści. Możesz o nich myśleć jak o hashtagach, które zwiększają wyszukiwalność treści dla czytelnika. Przykład słowa kluczowego: OpenAI, Duży Model Językowy, API, Agent itp.'},
        {'key': 'links', 'description': 'Kompletna lista wspomnianych linków i obrazów wraz z ich 1-zdaniowym opisem.'},
        {'key': 'resources', 'description': 'Narzędzia, platformy, zasoby wspomniane w artykule. Uwzględnij kontekst, w jaki sposób zasób może być użyty, jaki problem rozwiązuje lub jakąkolwiek uwagę, która pomoże czytelnikowi zrozumieć kontekst zasobu.'},
        {'key': 'takeaways', 'description': 'Główne punkty i cenne wnioski. Skup się tutaj na kluczowych wnioskach z artykułu, które same w sobie dostarczają wartości czytelnikowi (unikaj niejasnych i ogólnych stwierdzeń typu "to jest naprawdę ważne", ale podawaj konkretne przykłady i kontekst). Możesz również przedstawić wniosek w szerszym kontekście artykułu.'},
        {'key': 'context', 'description': 'Informacje ogólne i tło. Skup się tutaj na ogólnym kontekście artykułu, tak jakbyś wyjaśniał go komuś, kto nie czytał artykułu.'}
    ]

    # Uruchom wszystkie ekstrakcje współbieżnie
    extraction_tasks = [
        extract_information(title, article, item['key'], item['description'])
        for item in extraction_types
    ]
    
    print("Rozpoczynanie ekstrakcji informacji...")
    extracted_results_content = await asyncio.gather(*extraction_tasks)
    
    extracted_data = {}
    output_dir = os.path.join(BASE_DIR, "summary_output")
    os.makedirs(output_dir, exist_ok=True)

    # Przetwórz wyniki i zapisz do plików
    for i, item in enumerate(extraction_types):
        key = item['key']
        content = extracted_results_content[i]
        extracted_data[key] = content
        file_path = os.path.join(output_dir, f"{i + 1}_{key}.md")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Zapisano {key} do {file_path}")
        except Exception as e:
            print(f"Błąd podczas zapisu pliku {file_path}: {e}")

    # Tworzenie wersji roboczej podsumowania
    print("\nTworzenie wersji roboczej podsumowania...")
    draft_response = await draft_summary(
        title,
        article,
        extracted_data.get('context', ''),
        extracted_data.get('entities', ''),
        extracted_data.get('links', ''),
        extracted_data.get('topics', ''),
        extracted_data.get('takeaways', '')
    )
    draft_content = get_result(draft_response, 'final_answer') or draft_response # Użyj całej odpowiedzi jeśli tag nie istnieje
    draft_file_path = os.path.join(output_dir, '8_draft_summary.md')
    try:
        with open(draft_file_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)
        print(f"Zapisano wersję roboczą podsumowania do {draft_file_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu wersji roboczej: {e}")

    # Generowanie krytyki
    print("\nGenerowanie krytyki...")
    # Łączymy wszystkie wyekstrahowane dane jako jeden duży kontekst dla krytyki
    # W oryginalnym TS było Object.values(extractedData).join('\n\n')
    # Tutaj upewniamy się, że kolejność jest spójna z extraction_types dla lepszej czytelności
    critique_context_parts = [extracted_data.get(et['key'], '') for et in extraction_types]
    critique_context_full = "\n\n---\n\n".join(f"## {extraction_types[i]['key'].upper()}\n\n{part}" for i, part in enumerate(critique_context_parts))

    critique = await critique_summary(draft_content, article, critique_context_full)
    critique_file_path = os.path.join(output_dir, '9_summary_critique.md')
    try:
        with open(critique_file_path, 'w', encoding='utf-8') as f:
            f.write(critique)
        print(f"Zapisano krytykę do {critique_file_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu krytyki: {e}")

    # Tworzenie finalnego podsumowania
    print("\nTworzenie finalnego podsumowania...")
    final_summary_response = await create_final_summary(
        draft_content, # Przekazujemy treść wersji roboczej
        extracted_data.get('topics', ''),
        extracted_data.get('takeaways', ''),
        critique,
        extracted_data.get('context', '')
    )
    final_summary_content = get_result(final_summary_response, 'final_answer') or final_summary_response
    final_summary_file_path = os.path.join(output_dir, '10_final_summary.md')
    try:
        with open(final_summary_file_path, 'w', encoding='utf-8') as f:
            f.write(final_summary_content)
        print(f"Zapisano finalne podsumowanie do {final_summary_file_path}")
    except Exception as e:
        print(f"Błąd podczas zapisu finalnego podsumowania: {e}")

    print('\nZakończono wszystkie kroki. Wyniki zapisano w katalogu "summary_output".')

if __name__ == '__main__':
    # Uruchomienie głównej funkcji w pętli zdarzeń asyncio
    # W Python 3.7+ można użyć asyncio.run()
    asyncio.run(generate_detailed_summary())