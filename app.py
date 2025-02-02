# Import all required modules
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from joblib import dump, load
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from flask_talisman import Talisman

# Flask app configuration
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

# NLTK Resource Management
def download_nltk_resources():
    resources = [
        'punkt', 'wordnet', 'stopwords',
        'punkt_tab', 'omw-1.4'
    ]
    for resource in resources:
        try: nltk.data.find(resource)
        except LookupError: nltk.download(resource, quiet=True)
download_nltk_resources()

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'your_secret_key',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///users.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'UPLOAD_FOLDER': 'uploads',
    # 'MAX_CONTENT_LENGTH': 10 * 1024 * 1024  # 10MB
})

# Security and rate-limiting
# csrf = CSRFProtect(app)
# talisman = Talisman(app)
    'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
    'SEARCH_ENGINE_ID': os.environ.get('SEARCH_ENGINE_ID'),
    # 'MAX_CONTENT_LENGTH': 10 * 1024 * 1024
})

# Security extensions
# csrf = CSRFProtect(app)
# talisman = Talisman(
#     app,
#     content_security_policy={
#         'default-src': "'self'",
#         'script-src': ["'self'", "'unsafe-inline'"],
#         'style-src': ["'self'", "'unsafe-inline'"]
#     }
# )
# limiter = Limiter(app=app, key_func=get_remote_address)

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Allowed file types for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database model
# --- Database Model ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(120))
    preferences = db.Column(db.Text)
    chat_history = db.Column(db.Text)

    def set_preferences(self, preferences_dict):
        self.preferences = json.dumps(preferences_dict)

    def get_preferences(self):
        return json.loads(self.preferences) if self.preferences else {}

    def set_chat_history(self, chat_history_list):
        self.chat_history = json.dumps(chat_history_list)

    def get_chat_history(self):
        return json.loads(self.chat_history) if self.chat_history else []

with app.app_context():
    db.create_all()

# --- Authentication Routes ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# --- AI Model Configuration ---
training_data = [
    ("hello", "greeting"),
    ("hi there", "greeting"),
    ("good morning", "greeting"),
    ("hey", "greeting"),
    ("greetings", "greeting"),
    
    ("bye", "farewell"),
    ("see you later", "farewell"),
    ("goodnight", "farewell"),
    ("take care", "farewell"),
    
    ("thank you", "thanks"),
    ("thanks a lot", "thanks"),
    ("appreciate it", "thanks"),
    
    ("how are you?", "question"),
    ("what's your name?", "question"),
    ("what can you do?", "question"),
    
    ("help me", "help"),
    ("i need assistance", "help"),
    ("can you help?", "help"),
    
    ("tell me a joke", "joke"),
    ("make me laugh", "joke"),
    
    ("what time is it?", "time"),
    ("current time", "time"),
    
    ("weather today", "weather"),
    ("will it rain?", "weather"),
    
    ("latest news", "news"),
    ("what's happening?", "news"),
    
    ("play music", "music"),
    ("recommend a song", "music"),
]

# Enhanced responses
responses = {
    "greeting": "Hello! How can I assist you today?",
    "farewell": "Goodbye! Have a wonderful day!",
    "thanks": "You're welcome! Happy to help!",
    "question": "I'm an AI assistant here to help with your queries. What would you like to know?",
    "help": "Sure, I'd be happy to help. Please describe your issue.",
    "joke": "Why don't scientists trust atoms? Because they make up everything!",
    "time": "I don't have access to real-time data, but you can check your device's clock!",
    "weather": "I can't check real-time weather, but you can enable location services for weather apps.",
    "news": "For the latest news, I recommend checking trusted news websites or apps.",
    "music": "I can't play music directly, but I can suggest popular streaming platforms!",
    "unknown": "I'm not sure I understand. Could you rephrase that?",
}


# # Text preprocessing
# lemmatizer = WordNetLemmatizer()
# stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    try:
        if not isinstance(text, str) or len(text.strip()) == 0:
            return ""
        text = text.lower().translate(str.maketrans('', '', string.punctuation))
        words = nltk.word_tokenize(text)
        return ' '.join([
            lemmatizer.lemmatize(word) 
            for word in words 
            if word not in stop_words and len(word) > 2
        ])
    except Exception as e:
        print(f"Text processing error: {str(e)}")
        return ""

def train_model(save_model=True):
    global model, training_data
    # if len(training_data) < 50:
    #     raise ValueError("Insufficient training data")
    
    df = pd.DataFrame(training_data, columns=['text', 'label'])
    df = df.dropna()
    df['processed_text'] = df['text'].apply(
        lambda x: preprocess_text(x) if isinstance(x, str) else ""
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        df['processed_text'], df['label'], test_size=0.2, random_state=42
    )
    
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), max_features=500),
        SVC(kernel='linear', probability=True)
    )
    model.fit(X_train, y_train)
    
    if save_model:
        dump(model, 'chat_model.joblib')
    
    return model

# Load or train model
MODEL_PATH = 'chat_model.joblib'
model = load(MODEL_PATH) if os.path.exists(MODEL_PATH) else train_model()

# --- All Application Endpoints ---

# Authentication endpoints
@app.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Signup logic
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Profile management
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_picture = filename

        if 'preferences' in request.form:
            try:
                prefs = json.loads(request.form['preferences'])
                current_user.set_preferences(prefs)
            except json.JSONDecodeError:
                return "Invalid preferences format", 400

        db.session.commit()
        # Profile update logic
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)

# @app.route('/chat', methods=['POST'])
# @login_required
# def chat():
#     try:
#         data = request.get_json()
#         if not data or 'message' not in data:
#             return jsonify({'error': 'Invalid request'}), 400

#         user_input = data['message']
#         response = "This is a placeholder response"  # Replace with actual AI logic if needed

#         history = current_user.get_chat_history()
#         history.append({'user': user_input, 'response': response, 'timestamp': str(datetime.now())})
#         current_user.set_chat_history(history)
#         db.session.commit()

#         return jsonify({'response': response})

#     except Exception as e:
#         app.logger.error(f"Chat error: {str(e)}")
#         return jsonify({'error': 'Processing error'}), 500


# Chat endpoint
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        user_input = data['message']
        processed_input = preprocess_text(user_input)
        
        probabilities = model.predict_proba([processed_input])[0]
        max_prob = np.max(probabilities)
        predicted_label = model.predict([processed_input])[0]
        
        response = responses["unknown"] if max_prob < 0.6 else responses.get(predicted_label, responses["unknown"])
        
        # Update chat history
        history = current_user.get_chat_history()
        history.append({
            'user': user_input,
            'response': response,
            'timestamp': str(datetime.now()),
            'confidence': float(max_prob),
            'intent': predicted_label
        })
        current_user.set_chat_history(history)
        db.session.commit()

        return jsonify({
            'response': response,
            'confidence': float(max_prob),
            'intent': predicted_label
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Lofi Video Generation Route ---
# Media generation endpoints
@app.route('/generate_lofi', methods=['POST'])
@login_required
def generate_lofi_video():
    try:
        image_file = request.files.get('image')
        audio_file = request.files.get('audio')
        width = int(request.form.get('width', 800))
        height = int(request.form.get('height', 600))

        if not image_file or not audio_file:
            return jsonify({'error': 'Image and audio files are required'}), 400

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
        image_file.save(image_path)
        audio_file.save(audio_path)

        # Placeholder for actual lofi gif/video generation logic
        gif_path = image_path  # Replace with actual gif generation
        video_path = audio_path  # Replace with actual video generation

        return jsonify({
            'gif_url': f'/uploads/{os.path.basename(gif_path)}',
            'video_url': f'/uploads/{os.path.basename(video_path)}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- AI Video Generation Route ---
        # Lofi generation logic
        return jsonify({'message': 'Lofi content generated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_ai_video', methods=['POST'])
@login_required
def generate_ai_video():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Simulate video generation (Replace this with actual AI video generation logic)
        video_filename = f"generated_video_{current_user.id}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)

        # Simulated response
        return jsonify({
            'message': 'AI Video generated successfully!',
            'video_url': f'/uploads/{video_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- AI Music Generation Route ---
        # AI video generation logic
        return jsonify({'message': 'AI video generated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_ai_music', methods=['POST'])
@login_required
def generate_ai_music():
    try:
        mood = request.json.get('mood')
        if not mood:
            return jsonify({'error': 'Mood is required'}), 400

        # Simulate music generation (Replace this with actual AI music generation logic)
        music_filename = f"generated_music_{current_user.id}.mp3"
        music_path = os.path.join(app.config['UPLOAD_FOLDER'], music_filename)

        # Simulated response
        return jsonify({
            'message': 'AI Music generated successfully!',
            'music_url': f'/uploads/{music_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- File Handling ---
        # AI music generation logic
        return jsonify({'message': 'AI music generated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# File handling
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Model management
@app.route('/retrain', methods=['POST'])
@login_required
def retrain_model():
    if current_user.username != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        global model
        model = train_model()
        return jsonify({'message': 'Model retrained'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

# Main entry point
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if os.environ.get('FLASK_ENV') == 'production':
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(debug=True)
