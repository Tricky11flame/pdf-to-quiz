import os
import json
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Explicitly load .env.local
load_dotenv(dotenv_path=".env.local", override=True)

# --- CONFIGURATION ---
API_KEY = os.getenv("API_KEY")
subjects_raw = os.getenv("SUBJECTS", "")
SUBJECT_DIRS = [s.strip() for s in subjects_raw.split(",") if s.strip()]
MODEL_ID = os.getenv("MODEL_ID") 
MIN_QUESTION_THRESHOLD =int(os.getenv("MIN_QUESTION_THRESHOLD",5))
TIMEOUT = int(os.getenv("TIMEOUT",10))
# print(f"Loaded API Key: {API_KEY[:5]}... sub {SUBJECT_DIRS} ... model {MODEL_ID} ... min {MIN_QUESTION_THRESHOLD}") # Security check: print only prefix
client = genai.Client(api_key=API_KEY)

def generate_quiz_with_retry(text_content):
    while True:
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"Create a high-density quiz covering all technical facts in this text:\n\n{text_content}",
                config=types.GenerateContentConfig(
                    system_instruction="Output ONLY a raw JSON array of objects with keys 'q' and 'a'. No markdown.",
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                # Extract wait time from error message if possible (e.g., "51.351942089s")
                wait_match = re.search(r"retry in (\d+\.?\d*)s", error_msg)
                wait_seconds = float(wait_match.group(1)) if wait_match else 60
                
                print(f"!!! Quota Hit. Sleeping for {wait_seconds + TIMEOUT} seconds before retrying...")
                time.sleep(wait_seconds + TIMEOUT) # Added 5s buffer
                continue 
            else:
                # If it's a different error, raise it
                raise e

def process_subjects():
    for subject in SUBJECT_DIRS:
        text_dir = os.path.join(subject, "text")
        quiz_dir = os.path.join(subject, "quizes")
        if not os.path.exists(text_dir): continue
        os.makedirs(quiz_dir, exist_ok=True)
        
        subject_questions = []
        
        for filename in os.listdir(text_dir):
            if filename.endswith(".txt"):
                output_name = filename.replace(".txt", ".json")
                quiz_path = os.path.join(quiz_dir, output_name)
                
                # Health Check
                if os.path.exists(quiz_path):
                    try:
                        with open(quiz_path, "r") as f:
                            data = json.load(f)
                        if len(data) >= MIN_QUESTION_THRESHOLD:
                            print(f"Skipping {filename} (Healthy: {len(data)})")
                            subject_questions.extend(data)
                            continue
                    except: pass

                print(f"Processing: {subject} -> {filename}")
                with open(os.path.join(text_dir, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                
                try:
                    quiz_data = generate_quiz_with_retry(content)
                    print(f"Generated {len(quiz_data)} questions.")
                    
                    with open(quiz_path, "w") as out:
                        json.dump(quiz_data, out, indent=2)
                    
                    subject_questions.extend(quiz_data)
                    time.sleep(TIMEOUT) # Baseline rate limit
                except Exception as e:
                    print(f"Fatal error on {filename}: {e}")

        if subject_questions:
            full_path = os.path.join(subject, "fullQuiz.json")
            with open(full_path, "w") as f:
                json.dump(subject_questions, f, indent=2)

if __name__ == "__main__":
    process_subjects()