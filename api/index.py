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
import logging
import pickle
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Validate environment variables
if not all([SUPABASE_URL, SUPABASE_API_KEY, HUGGINGFACE_API_KEY]):
    logger.error("Missing required environment variables")
    raise ValueError("SUPABASE_URL, SUPABASE_API_KEY, and HUGGINGFACE_API_KEY must be set")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Initialize QwenChatbot
class QwenChatbot:
    def __init__(self, model_name="meta-llama/Llama-3-8b-chat-hf", use_api=True):
        self.use_api = use_api
        self.history = []
        self.model_name = model_name
        self.fallback_models = [
            "meta-llama/Llama-3-8b-chat-hf",
            "Qwen/Qwen1.5-0.5B-Instruct",
            "mistralai/Mixtral-8x7B-Instruct-v0.1"
        ]
        if not use_api:
            try:
                logger.info(f"Loading local model: {model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=HUGGINGFACE_API_KEY)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name, torch_dtype="auto", device_map="auto", token=HUGGINGFACE_API_KEY
                )
                logger.info(f"Successfully loaded local model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {str(e)}")
                raise
        else:
            logger.info(f"Using Hugging Face Inference API for {model_name}")
            self.api_endpoint = f"https://api-inference.huggingface.co/models/{model_name}"

    def generate_response(self, user_input, enable_thinking=True):
        logger.info(f"Generating response for input: {user_input[:50]}...")
        if "/no_think" in user_input:
            enable_thinking = False
            user_input = user_input.replace("/no_think", "").strip()
        elif "/think" in user_input:
            enable_thinking = True
            user_input = user_input.replace("/think", "").strip()

        messages = self.history + [{"role": "user", "content": user_input}]

        if self.use_api:
            for model in [self.model_name] + self.fallback_models:
                try:
                    api_endpoint = f"https://api-inference.huggingface.co/models/{model}"
                    logger.info(f"Trying API endpoint: {api_endpoint}")
                    for attempt in range(3):
                        try:
                            response = requests.post(
                                api_endpoint,
                                json={
                                    "inputs": "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages),
                                    "parameters": {
                                        "max_new_tokens": 2048,
                                        "do_sample": True,
                                        "top_k": 20,
                                        "min_p": 0.0,
                                        **({"temperature": 0.6, "top_p": 0.95} if enable_thinking else {"temperature": 0.7, "top_p": 0.8})
                                    }
                                },
                                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
                            )
                            response.raise_for_status()
                            response_text = response.json()[0]["generated_text"].split("assistant:")[-1].strip()
                            logger.info(f"API response received successfully from {model}")
                            break
                        except requests.exceptions.HTTPError as e:
                            if '429' in str(e) and attempt < 2:  # Rate limit
                                logger.warning(f"Rate limit hit for {model}, retrying in {2 ** attempt} seconds...")
                                time.sleep(2 ** attempt)
                            else:
                                raise
                    break
                except Exception as e:
                    logger.warning(f"API request to {model} failed: {str(e)}")
                    if model == self.fallback_models[-1]:
                        raise Exception(f"All API models failed: {str(e)}")
            else:
                raise Exception("No API models available")
        else:
            try:
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
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
                response_text = self.tokenizer.decode(response_ids, skip_special_tokens=True).strip()
                logger.info("Local model response generated successfully")
            except Exception as e:
                logger.error(f"Model generation failed: {str(e)}")
                raise Exception(f"Model generation failed: {str(e)}")

        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response_text})
        if len(self.history) > 20:
            self.history = self.history[-20:]

        return response_text

# Initialize chatbot with fallback to API
try:
    chatbot = QwenChatbot(model_name="meta-llama/Llama-3-8b-chat-hf", use_api=True)
except Exception as e:
    logger.warning(f"Model initialization failed: {str(e)}. Falling back to Qwen model.")
    chatbot = QwenChatbot(model_name="Qwen/Qwen1.5-0.5B-Instruct", use_api=True)

# Dataset cache
dataset_cache = None

# Helper function to load and cache dataset
def load_dataset():
    global dataset_cache
    cache_file = "dataset_cache.pkl"
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "rb") as f:
                dataset_cache = pickle.load(f)
            logger.info(f"Loaded cached dataset from {cache_file} with {len(dataset_cache)} records")
            if dataset_cache:
                logger.info(f"Sample records: {dataset_cache[:3]}")
            return dataset_cache
        except Exception as e:
            logger.warning(f"Failed to load cached dataset: {str(e)}. Reloading from source.")
    
    try:
        logger.info("Fetching dataset metadata")
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
        logger.info(f"Downloading Parquet file from {parquet_url}")
        parquet_response = requests.get(parquet_url)
        parquet_response.raise_for_status()

        with open("temp.parquet", "wb") as f:
            f.write(parquet_response.content)

        logger.info("Reading Parquet file")
        df = pd.read_parquet("temp.parquet")
        # Filter records with valid prompts
        dataset_cache = [
            record for record in df.to_dict(orient="records")
            if record.get("prompt") and isinstance(record["prompt"], str) and len(record["prompt"].strip()) > 0
        ]
        if not dataset_cache:
            raise ValueError("No records with valid prompts found in dataset")
        
        # Cache to disk
        with open(cache_file, "wb") as f:
            pickle.dump(dataset_cache, f)
        logger.info(f"Dataset cached to {cache_file} with {len(dataset_cache)} valid records")
        logger.info(f"Sample records: {dataset_cache[:3]}")
        
        os.remove("temp.parquet")
        return dataset_cache
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise Exception(f"Error loading dataset: {str(e)}")

@app.route("/generate", methods=["GET"])
def generate():
    search = request.args.get("search")
    if not search:
        logger.warning("Generate endpoint called without search query")
        return jsonify({"message": "Search query is required"}), 400

    try:
        response = chatbot.generate_response(search)
        logger.info("Generate endpoint response sent")
        return jsonify({"message": response}), 200
    except Exception as e:
        logger.error(f"Generate endpoint failed: {str(e)}")
        return jsonify({"message": f"Failed to generate response: {str(e)}"}), 500

@app.route("/api/profile", methods=["GET"])
def profile():
    try:
        response = supabase.auth.get_user()
        if hasattr(response, "error") and response.error:
            raise Exception(response.error.message)
        logger.info("Profile retrieved successfully")
        return jsonify({"user": response.user.to_dict()}), 200
    except Exception as e:
        logger.error(f"Profile endpoint failed: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    phone = data.get("phone")

    if not email or not password or not name:
        logger.warning("Signup endpoint called with missing required fields")
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
        if hasattr(response, "error") and response.error:
            raise Exception(response.error.message)
        logger.info(f"User signed up successfully: {email}")
        return jsonify({
            "message": "User signed up successfully",
            "user": response.user.to_dict(),
            "token": response.session.to_dict() if response.session else None
        }), 200
    except Exception as e:
        logger.error(f"Signup endpoint failed: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/api/auth/signin", methods=["POST"])
def signin():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        logger.warning("Signin endpoint called with missing required fields")
        return jsonify({"message": "Email and password are required"}), 400

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if hasattr(response, "error") and response.error:
            raise Exception(response.error.message)
        logger.info(f"User signed in successfully: {email}")
        return jsonify({
            "message": "User logged in successfully",
            "user": response.user.to_dict(),
            "token": response.session.to_dict() if response.session else None
        }), 200
    except Exception as e:
        logger.error(f"Signin endpoint failed: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/api/image-pair", methods=["GET"])
def image_pair():
    try:
        records = load_dataset()
        random_record = random.choice(records)
        logger.info("Image pair retrieved successfully")
        return jsonify({"pair": random_record}), 200
    except Exception as e:
        logger.error(f"Image pair endpoint failed: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/api/generate-image", methods=["GET"])
def generate_image():
    try:
        prompt = request.args.get("prompt")
        random_record = None
        if not prompt:
            records = load_dataset()
            random_record = random.choice(records)
            prompt = random_record.get("prompt")

        if not prompt or not isinstance(prompt, str) or not prompt.strip():
            logger.warning(f"Invalid or missing prompt in record: {random_record}")
            prompt = "A scenic landscape with mountains and a river"
            logger.info(f"Using fallback prompt: {prompt}")

        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        image_models = [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5"
        ]
        image_response = None
        for model in image_models:
            for attempt in range(3):
                try:
                    logger.info(f"Trying image model: {model}")
                    image_response = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}",
                        json={"inputs": prompt},
                        headers={
                            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                            "Content-Type": "application/json"
                        }
                    )
                    image_response.raise_for_status()
                    logger.info(f"Image generated successfully with {model}")
                    break
                except requests.exceptions.HTTPError as e:
                    if '429' in str(e) and attempt < 2:  # Rate limit
                        logger.warning(f"Rate limit hit for {model}, retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)
                    elif '404' in str(e):
                        logger.warning(f"Model {model} not found, trying next model")
                        break
                    else:
                        raise
            if image_response:
                break
        if not image_response:
            raise Exception("All image generation models failed or are unavailable")

        image_base64 = base64.b64encode(image_response.content).decode("utf-8")
        logger.info("Image encoded successfully")
        return jsonify({
            "prompt": prompt,
            "generatedImage": f"data:image/png;base64,{image_base64}",
            "originalPair": random_record or {}
        }), 200
    except Exception as e:
        logger.error(f"Generate image endpoint failed: {str(e)}")
        return jsonify({"message": f"Failed to generate image: {str(e)}"}), 500

@app.route("/api/submit-preference", methods=["POST"])
def submit_preference():
    data = request.get_json()
    pair_id = data.get("pairId")
    preference = data.get("preference")
    user_id = data.get("userId")

    if not pair_id or not preference or not user_id:
        logger.warning("Submit preference endpoint called with missing required fields")
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

        logger.info("Preference submitted successfully")
        return jsonify({"message": "Preference saved successfully"}), 200
    except Exception as e:
        logger.error(f"Submit preference endpoint failed: {str(e)}")
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

        logger.info("Preference stats retrieved successfully")
        return jsonify({"stats": stats}), 200
    except Exception as e:
        logger.error(f"Preference stats endpoint failed: {str(e)}")
        return jsonify({"message": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server on port 3001")
    app.run(host="0.0.0.0", port=3001)