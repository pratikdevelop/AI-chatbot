import os
import json
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# Define the path where the trained model will be saved
MODEL_PATH = 'chatbot_model.pkl'

# Initial training data (hardcoded list of text-intent pairs)
initial_training_data = [
    ("hello", "greeting"), ("hi there", "greeting"), ("hey", "greeting"), ("good morning", "greeting"),
    ("bye", "farewell"), ("goodbye", "farewell"), ("see you", "farewell"),
    ("thanks", "thanks"), ("thank you", "thanks"), ("appreciate it", "thanks"),
    ("help", "help"), ("assist me", "help"), ("what can you do", "help"),
    ("tell me a joke", "joke"), ("funny", "joke"), ("make me laugh", "joke"),
    ("who are you", "identity"), ("what are you", "identity"),
    ("search", "search"), ("look up", "search"), ("find", "search"),
    ("what is", "wiki"), ("tell me about", "wiki"), ("explain", "wiki")
]

# Function to train and save the model
def train_model(texts, labels):
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(texts, labels)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved to {MODEL_PATH}")

# Check if a command-line argument (JSON file path) is provided
if len(sys.argv) > 1:
    json_file = sys.argv[1]
    try:
        # Load the JSON file containing new training data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Validate JSON structure
        if 'training_data' not in data:
            print("Error: JSON must contain 'training_data' key")
            sys.exit(1)
        
        training_data = data['training_data']
        if not isinstance(training_data, list) or not all(isinstance(item, dict) and 'text' in item and 'intent' in item for item in training_data):
            print("Error: 'training_data' must be a list of objects with 'text' and 'intent'")
            sys.exit(1)
        
        # Extract texts and labels from the JSON data
        texts = [item['text'] for item in training_data]
        labels = [item['intent'] for item in training_data]
        
        # Train the model with the new data
        train_model(texts, labels)
    
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)
else:
    # If no JSON file is provided, check if the model exists
    if not os.path.exists(MODEL_PATH):
        # If model doesn't exist, train with initial data
        texts, labels = zip(*initial_training_data)
        train_model(texts, labels)
    else:
        # If model exists, inform the user
        print("Model already trained. To retrain, provide a JSON file with new training data.")