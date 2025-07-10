import google.generativeai as genai
import csv
import os
import json
import time # To add delays between API calls
import argparse
import random

# ==============================================================================
# <<<--- (1) USER CONFIGURATION: EDIT THIS SECTION FOR EACH FILE ---<<<
# ==============================================================================
# Path to your plain text (.txt) input file (one lingo entry per line).
# If the file is in the same directory as this script, just use its name.
# Otherwise, provide the full path.
INPUT_FILE_PATH = "aussielingo.txt"  # <<< REPLACE with "arg.txt" or your exact input file name

# Desired name for the structured CSV output file.
OUTPUT_CSV_PATH = "aussielingo.csv" # <<< REPLACE if you want a different output name

# Language code for ALL entries in the INPUT_FILE_PATH.
LANGUAGE_CODE_FOR_FILE = "en-AU" # <<< REPLACE with 'es-AR' for Argentina, 'en-AU' for Australia, etc.
# ==============================================================================
# --- END OF USER CONFIGURATION ---
# ==============================================================================

# --- API Key Setup ---
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
except KeyError:
    print("💥 GOOGLE_API_KEY environment variable not set.")
    print("Please set it in your terminal before running the script:")
    print("  For macOS/Linux: export GOOGLE_API_KEY='YOUR_API_KEY_HERE'")
    print("  For Windows CMD: set GOOGLE_API_KEY=\"YOUR_API_KEY_HERE\"")
    print("  For Windows PowerShell: $env:GOOGLE_API_KEY=\"YOUR_API_KEY_HERE\"")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)
# Using Gemini 1.5 Flash. You can try 'gemini-1.5-pro-latest' if results need improvement.
model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')

# Category codes your Django model expects (ensure these match models.py choices)
# Updated to match the choices in the Entry model
VALID_CATEGORY_CODES = [
    'SLANG', 'IDIOM', 'SAYING', 'TWISTER', 'INSULT', 'WORD', 'OTHER'
]

def process_text_with_ai(raw_text_entry, language_code_param):
    """
    Sends a raw text entry to the Gemini API for structuring and categorization.
    Returns a dictionary or None.
    """
    print(f"    Sending to AI: '{raw_text_entry[:70]}...'")
    category_options_str = ", ".join(VALID_CATEGORY_CODES)
    prompt = f"""
    You are an expert linguist and data processor.
    Analyze the following lingo entry, which is for the language code '{language_code_param}'.
    The entry text might contain a term/phrase, its meaning/explanation, usage notes, part of speech, and potentially implied region or tags.

    Raw Lingo Entry:
    ---
    {raw_text_entry}
    ---

    Based on the text, extract the following information and structure it as a JSON object:
    1.  "term": The main lingo term or phrase.
    2.  "region_code": The specific city or region for '{language_code_param}' if clearly implied (e.g., "Buenos Aires", "Bavaria"). If general for the language, leave blank or use a general region if applicable (e.g. "Argentina" for es-AR if no sub-region).
    3.  "category": Choose ONLY ONE MOST appropriate category code from this exact list: [{category_options_str}]. Do not invent new categories. If unsure, use 'OTHER'.
    4.  "part_of_speech": The grammatical part of speech if applicable (e.g., "noun", "verb", "adjective", "phrase"). Leave blank if not clear.
    5.  "notes": A comprehensive definition, explanation of meaning, and any cultural context or usage information from the raw text.
    6.  "tags": Suggest 1-3 relevant single-word or short multi-word tags (comma-separated, e.g., "Informal,Food,Humorous").

    Your output MUST be a valid JSON object. Example:
    {{
        "term": "Che Pibe",
        "region_code": "Argentina",
        "category": "ENDEARMENT",
        "part_of_speech": "phrase",
        "notes": "A common way to call a young person or kid in Argentina. Often used informally.",
        "tags": "Informal,Youth,Argentina"
    }}

    If a field cannot be reliably extracted, use an empty string "" for its value.
    Ensure "category" is one of the valid codes.
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2) # Lower temp for more factual output
        )
        cleaned_response_text = response.text.strip()
        if cleaned_response_text.startswith("```json"):
            cleaned_response_text = cleaned_response_text[7:]
        if cleaned_response_text.endswith("```"):
            cleaned_response_text = cleaned_response_text[:-3]
        
        ai_output = json.loads(cleaned_response_text.strip())

        if 'category' in ai_output and ai_output['category'] not in VALID_CATEGORY_CODES:
            print(f"    AI returned invalid category: '{ai_output['category']}'. Forcing to 'OTHER'. Original text: '{raw_text_entry[:50]}...'")
            ai_output['category'] = 'OTHER'
        elif 'category' not in ai_output or not ai_output['category']:
             print(f"    AI did not return a category. Defaulting to 'OTHER'. Original text: '{raw_text_entry[:50]}...'")
             ai_output['category'] = 'OTHER'

        print(f"    AI structured: {ai_output}")
        return ai_output

    except json.JSONDecodeError as json_err:
        print(f"    Error decoding JSON from AI: {json_err}")
        print(f"    AI Raw Response: {response.text if 'response' in locals() else 'No response text'}")
        return None
    except Exception as e:
        raw_response_text = "No response object"
        if 'response' in locals() and response:
            try: raw_response_text = response.text
            except: raw_response_text = "Could not get raw response text"
        print(f"    Error calling AI: {e}. Raw Response: {raw_response_text}")
        return None


def generate_quiz_questions(processed_rows_data, output_json_path):
    """
    Generate quiz questions with plausible distractors from processed lingo data.
    Each question will have 1 correct answer and 3 distractors (from other entries' notes).
    Output is a JSON file with a list of questions.
    """
    questions = []
    all_notes = [row['notes'] for row in processed_rows_data]
    for i, row in enumerate(processed_rows_data):
        correct = row['notes']
        distractors = set()
        # Sample distractors from other notes
        candidates = [n for idx, n in enumerate(all_notes) if idx != i and n != correct and n]
        random.shuffle(candidates)
        for cand in candidates:
            if len(distractors) >= 3:
                break
            # Avoid distractors that are too similar to the correct answer
            if cand.lower()[:10] != correct.lower()[:10]:
                distractors.add(cand)
        # Fallback: if not enough, fill with generic but unique placeholders
        while len(distractors) < 3:
            distractors.add(f"Option {len(distractors)+1}")
        options = list(distractors) + [correct]
        random.shuffle(options)
        questions.append({
            'term': row['term'],
            'question': f"What does '{row['term']}' mean?",
            'options': options,
            'correct': options.index(correct),
            'explanation': correct
        })
    # Write to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Quiz questions with distractors written to {output_json_path}")

def create_structured_csv(input_path, output_path, lang_code):
    print(f"\nProcessing '{input_path}' for language '{lang_code}'...")
    output_headers = ['language_code', 'category', 'region_code', 'term', 'part_of_speech', 'notes', 'tags']
    processed_rows_data = []
    total_lines_read = 0
    ai_errors = 0

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            for line_num, raw_line in enumerate(infile, 1):
                total_lines_read += 1
                raw_entry_text = raw_line.strip()
                if not raw_entry_text:
                    continue

                structured_data = process_text_with_ai(raw_entry_text, lang_code)

                # Only include entries with a non-empty term, non-empty notes, and category not OTHER
                if structured_data:
                    term = structured_data.get('term', '').strip()
                    notes = structured_data.get('notes', '').strip()
                    category = structured_data.get('category', 'OTHER').upper()
                    if term and notes and category != 'OTHER':
                        processed_rows_data.append({
                            'language_code': lang_code,
                            'category': category,
                            'region_code': structured_data.get('region_code', ''),
                            'term': term,
                            'part_of_speech': structured_data.get('part_of_speech', ''),
                            'notes': notes,
                            'tags': structured_data.get('tags', '')
                        })
                    else:
                        print(f"  Skipping line {line_num} due to missing term, notes, or category OTHER.")
                else:
                    print(f"  Skipping line {line_num} ('{raw_entry_text[:50]}...') due to AI processing error.")
                    ai_errors += 1
                
                if total_lines_read > 0 and total_lines_read % 5 == 0: # More frequent feedback
                    print(f"    ...processed {total_lines_read} lines from input file so far.")
                time.sleep(1.1) # Be respectful of API rate limits (e.g., Gemini Flash free tier is often 60 QPM)

    except FileNotFoundError:
        print(f"ERROR: Input file not found: '{input_path}'")
        return
    except Exception as e:
        print(f"ERROR: An unexpected error occurred reading input file: {e}")
        return

    if processed_rows_data:
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_headers)
                writer.writeheader()
                writer.writerows(processed_rows_data)
            print(f"\nSuccessfully wrote {len(processed_rows_data)} entries to '{output_path}'")
            # Generate quiz questions JSON with distractors
            quiz_json_path = output_path.replace('.csv', '_quiz.json')
            generate_quiz_questions(processed_rows_data, quiz_json_path)
        except Exception as e:
            print(f"ERROR: Could not write to output CSV file '{output_path}': {e}")
    else:
        print("\nNo data was processed to write to CSV.")

    print(f"Finished processing '{input_path}'.")
    print(f"Total lines read from input: {total_lines_read}")
    print(f"AI processing errors encountered: {ai_errors}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process raw lingo data into structured CSV using Gemini AI.')
    parser.add_argument('--input', type=str, default=INPUT_FILE_PATH, help='Path to the input .txt file')
    parser.add_argument('--output', type=str, default=OUTPUT_CSV_PATH, help='Path to the output .csv file')
    parser.add_argument('--lang', type=str, default=LANGUAGE_CODE_FOR_FILE, help='Language code for the entries (e.g., es-AR, en-AU)')
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    lang_code = args.lang

    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found at '{input_file}'")
        print("Please create the input file and/or correct the input file path.")
    elif "YOUR_API_KEY" in GOOGLE_API_KEY or not GOOGLE_API_KEY:
         print("ERROR: GOOGLE_API_KEY is not properly set as an environment variable.")
         print("Please set it in your terminal before running the script.")
    else:
        print("Starting Lingo Processing Script...")
        create_structured_csv(input_file, output_file, lang_code)
        print(f"\nNext step: If '{output_file}' looks good, import it into Django using:")
        print(f"  python manage.py import_lingo \"{output_file}\"")