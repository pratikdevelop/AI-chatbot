from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
import random
import base64
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Initialize QwenChatbot
class QwenChatbot:
    def __init__(self, model_name="Qwen/Qwen2-7B-Instruct"):  # Smaller model for testing
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype="auto", device_map="auto"
        )
        self.history = []

    def generate_response(self, user_input, enable_thinking=True):
        if "/no_think" in user_input:
            enable_thinking = False
            user_input = user_input.replace("/no_think", "").strip()
        elif "/think" in user_input:
            enable_thinking = True
            user_input = user_input.replace("/think", "").strip()

        messages = self.history + [{"role": "user", "content": user_input}]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        
        generate_kwargs = {
            "max_new_tokens": 32768,
            "do_sample": True,
            "top_k": 20,
            "min_p": 0.0,
            **({"temperature": 0.6, "top_p": 0.95} if enable_thinking else {"temperature": 0.7, "top_p": 0.8})
        }

        response_ids = self.model.generate(**inputs, **generate_kwargs)[0][len(inputs.input_ids[0]):].tolist()
        response = self.tokenizer.decode(response_ids, skip_special_tokens=True).strip()

        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})

        # Limit history to prevent memory issues
        if len(self.history) > 20:
            self.history = self.history[-20:]

        return response

chatbot = QwenChatbot()

# Cache for dataset records
dataset_cache = None

# Helper function to load and cache dataset
def load_dataset():
    global dataset_cache
    if dataset_cache is not None:
        return dataset_cache

    try:
        metadata_response = requests.get(
            "https://huggingface.co/api/datasets/data-is-better-together/image-preferences-results"
        )
        metadata_response.raise_for_status()
        metadata = metadata_response.json()

        parquet_file = next(
            (file for file in metadata["siblings"] if "train-00000-of-00001.parquet" in file["rfilename"]), None
        )
        if not parquet_file:
            raise ValueError("Parquet file not found in dataset")

        parquet_url = (
            f"https://huggingface.co/datasets/data-is-better-together/image-preferences-results/resolve/main/{parquet_file['rfilename']}"
        )
        parquet_response = requests.get(parquet_url)
        parquet_response.raise_for_status()

        # Save Parquet file temporarily
        with open("temp.parquet", "wb") as f:
            f.write(parquet_response.content)

        # Read Parquet file with pandas
        df = pd.read_parquet("temp.parquet")
        dataset_cache = df.to_dict(orient="records")

        # Clean up temporary file
        os.remove("temp.parquet")

        return dataset_cache
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")

@app.route("/generate", methods=["GET"])
def generate():
    search = request.args.get("search")
    if not search:
        return jsonify({"message": "Search query is required"}), 400

    try:
        response = chatbot.generate_response(search)
        return jsonify({"message": response}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/profile", methods=["GET"])
def profile():
    try:
        response = supabase.auth.get_user()
        return jsonify({"user": response.user.to_dict()}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    phone = data.get("phone")

    if not email or not password or not name:
        return jsonify({"message": "Email, password, and name are required"}), 400

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name,
                    "phone": phone
                }
            }
        })
        return jsonify({
            "message": "User signed up successfully",
            "user": response.user.to_dict(),
            "token": response.session.to_dict() if response.session else None
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/auth/signin", methods=["POST"])
def signin():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        print("Sign-in response:", response.session.to_dict())
        return jsonify({
            "message": "User logged in successfully",
            "user": response.user.to_dict(),
            "token": response.session.to_dict() if response.session else None
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/image-pair", methods=["GET"])
def image_pair():
    try:
        records = load_dataset()
        random_record = random.choice(records)
        return jsonify({"pair": random_record}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/generate-image", methods=["GET"])
def generate_image():
    try:
        records = load_dataset()
        random_record = random.choice(records)
        prompt = random_record.get("prompt")

        if not prompt:
            return jsonify({"message": "Prompt not found in record"}), 400

        image_response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
            json={"inputs": prompt},
            headers={
                "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        image_response.raise_for_status()

        image_base64 = base64.b64encode(image_response.content).decode("utf-8")
        return jsonify({
            "prompt": prompt,
            "generatedImage": f"data:image/png;base64,{image_base64}",
            "originalPair": random_record
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/submit-preference", methods=["POST"])
def submit_preference():
    data = request.get_json()
    pair_id = data.get("pairId")
    preference = data.get("preference")
    user_id = data.get("userId")

    if not pair_id or not preference or not user_id:
        return jsonify({"message": "pairId, preference, and userId are required"}), 400

    try:
        response = supabase.table("user_preferences").insert({
            "pair_id": pair_id,
            "preference": preference,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        if hasattr(response, "error") and response.error:
            raise Exception(response.error.message)

        return jsonify({"message": "Preference saved successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/preference-stats", methods=["GET"])
def preference_stats():
    try:
        response = supabase.table("user_preferences").select("preference").execute()
        if hasattr(response, "error") and response.error:
            raise Exception(response.error.message)

        stats = {}
        for row in response.data:
            preference = row["preference"]
            stats[preference] = stats.get(preference, 0) + 1

        return jsonify({"stats": stats}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)