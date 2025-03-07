import os
import json
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
from datasets import load_dataset

# Path where the trained model will be saved
MODEL_PATH = 'chatbot_model.pkl'

# Initial hardcoded training data
initial_training_data = [
    ("hello", "greeting"), ("hi there", "greeting"), ("hey", "greeting"), ("good morning", "greeting"),
    ("bye", "farewell"), ("goodbye", "farewell"), ("see you", "farewell"),
    ("thanks", "thanks"), ("thank you", "thanks"), ("appreciate it", "thanks"),
    ("help", "help"), ("assist me", "help"), ("what can you do", "help"),
    ("tell me a joke", "joke"), ("funny", "joke"), ("make me laugh", "joke"),
    ("who are you", "identity"), ("what are you", "identity"),
    ("search", "search"), ("look up", "search"), ("find", "search"),
    ("what is", "wiki"), ("tell me about", "wiki"), ("explain", "wiki"),
    ("how are you", "greeting"), ("what's up", "greeting"), ("hi buddy", "greeting"),
    ("catch you later", "farewell"), ("see ya", "farewell"),
    ("thank you so much", "thanks"), ("grateful", "thanks"),
    ("can you assist", "help"), ("I need help", "help"),
    ("say something funny", "joke"), ("crack a joke", "joke"),
    ("what’s your name", "identity"), ("are you human", "identity"),
    ("search online", "search"), ("find info", "search"),
    ("define", "wiki"), ("what’s the meaning of", "wiki")
]

# Load and process Hugging Face dataset
def load_huggingface_data():
    print("Loading Hugging Face dataset...")
    ds = load_dataset("fka/awesome-chatgpt-prompts")
    prompts = ds['train']['prompt']
    training_data = []
    for prompt in prompts:
        prompt = prompt.lower()
        if "joke" in prompt or "funny" in prompt or "humor" in prompt:
            intent = "joke"
        elif "search" in prompt or "find" in prompt or "look up" in prompt:
            intent = "search"
        elif "what is" in prompt or "explain" in prompt or "tell me about" in prompt:
            intent = "wiki"
        elif "help" in prompt or "assist" in prompt or "support" in prompt:
            intent = "help"
        elif "thank" in prompt or "grateful" in prompt or "appreciate" in prompt:
            intent = "thanks"
        elif "hello" in prompt or "hi" in prompt or "greet" in prompt:
            intent = "greeting"
        elif "bye" in prompt or "goodbye" in prompt or "later" in prompt:
            intent = "farewell"
        elif "who" in prompt or "what are you" in prompt or "identity" in prompt:
            intent = "identity"
        else:
            intent = "unknown"
        training_data.append((prompt, intent))
    print(f"Processed {len(training_data)} prompts from Hugging Face dataset.")
    return training_data

# Train and save the model
def train_model(texts, labels):
    print("Training model...")
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(texts, labels)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")

if __name__ == "__main__":
    # Load Hugging Face data
    hf_training_data = load_huggingface_data()
    
    # Combine with initial data
    training_data = initial_training_data + hf_training_data
    print(f"Initial training data: {len(initial_training_data)} examples.")
    
    # Check for additional JSON data via command-line argument
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        print(f"Loading additional data from {json_file}...")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            if 'training_data' not in data:
                print("Error: JSON must contain 'training_data' key")
                sys.exit(1)
            json_training_data = data['training_data']
            if not all(isinstance(item, dict) and 'text' in item and 'intent' in item for item in json_training_data):
                print("Error: 'training_data' must be a list of objects with 'text' and 'intent'")
                sys.exit(1)
            additional_data = [(item['text'], item['intent']) for item in json_training_data]
            training_data += additional_data
            print(f"Added {len(additional_data)} examples from JSON file.")
        except Exception as e:
            print(f"Error loading JSON: {e}")
            sys.exit(1)
    
    print(f"Total training examples: {len(training_data)}")
    
    # Extract texts and labels
    texts, labels = zip(*training_data)
    
    # Train and save the model
    if os.path.exists(MODEL_PATH):
        print(f"Warning: Existing model at {MODEL_PATH} will be overwritten.")
    train_model(texts, labels)