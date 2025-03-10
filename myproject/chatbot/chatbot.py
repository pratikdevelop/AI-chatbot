import joblib
import os

MODEL_PATH = '/home/pc-25/Music/AI-chatbot/chatbot_model.pkl'

def load_chatbot_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Please train it in Flask first.")
    return joblib.load(MODEL_PATH)