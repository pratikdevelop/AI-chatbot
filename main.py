# # from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, redirect, url_for
# # from flask_sqlalchemy import SQLAlchemy
# # from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# # from werkzeug.security import generate_password_hash, check_password_hash
# # from flask_bcrypt import Bcrypt
# # import os
# # from PIL import Image, ImageFilter
# # from moviepy import *
# # from werkzeug.utils import secure_filename
# # import json
# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from sklearn.naive_bayes import MultinomialNB
# # from sklearn.pipeline import make_pipeline
# # # Initialize the app and extensions
# # app = Flask(__name__)
# # app.config['UPLOAD_FOLDER'] = 'uploads'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database for storing users
# # app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for session management
# # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # # Initialize database and login manager
# # db = SQLAlchemy(app)
# # login_manager = LoginManager(app)
# # login_manager.login_view = 'login'  # Redirect to login if not authenticated
# # bcrypt = Bcrypt(app)


# # GOOGLE_API_KEY = "your_google_api_key"  # Replace with your API key
# # SEARCH_ENGINE_ID = "your_search_engine_id"  # Replace with your Search Engine ID

# # # Training data for the ML model
# # training_data = [
# #     ("hello", "greeting"),
# #     ("hi", "greeting"),
# #     ("hey there", "greeting"),
# #     ("good morning", "greeting"),
# #     ("bye", "farewell"),
# #     ("goodbye", "farewell"),
# #     ("see you later", "farewell"),
# #     ("thank you", "thanks"),
# #     ("thanks a lot", "thanks"),
# #     ("appreciate it", "thanks"),
# #     ("how are you?", "question"),
# #     ("what is your name?", "question"),
# #     ("can you help me?", "help"),
# #     ("i need assistance", "help"),
# #     ("tell me a joke", "joke"),
# #     ("make me laugh", "joke"),
# #     ("what time is it?", "time"),
# #     ("what's the date today?", "time"),
# # ]



# # # Predefined responses for each intent
# # responses = {
# #     "greeting": "Hello! How can I assist you today?",
# #     "farewell": "Goodbye! Have a great day!",
# #     "thanks": "You're welcome!",
# #     "question": "I'm here to answer your questions. What do you need help with?",
# #     "help": "Of course! Tell me what you need assistance with.",
# #     "joke": "Why don’t scientists trust atoms? Because they make up everything!",
# #     "time": "I'm not a clock, but I can help you with other things!",
# #     "unknown": "I'm sorry, I didn't understand that.",
# # }

# # # Separate training data into texts and labels
# # texts, labels = zip(*training_data)

# # # Create and train the model
# # model = make_pipeline(TfidfVectorizer(), MultinomialNB())
# # model.fit(texts, labels)

# # # Define the User model with additional fields
# # class User(UserMixin, db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     username = db.Column(db.String(100), unique=True, nullable=False)
# #     email = db.Column(db.String(120), unique=True, nullable=False)
# #     password = db.Column(db.String(100), nullable=False)
# #     profile_picture = db.Column(db.String(120), nullable=True)  # Optional profile picture field
# #     preferences = db.Column(db.Text, nullable=True)  # Store preferences as JSON or text
# #     chat_history = db.Column(db.Text, nullable=True)  # Store chat history as JSON or text

# #     def set_preferences(self, preferences_dict):
# #         """Set preferences as a JSON string."""
# #         self.preferences = json.dumps(preferences_dict)

# #     def get_preferences(self):
# #         """Get preferences as a dictionary."""
# #         if self.preferences:
# #             return json.loads(self.preferences)
# #         return {}

# #     def set_chat_history(self, chat_history_list):
# #         """Set chat history as a JSON string."""
# #         self.chat_history = json.dumps(chat_history_list)

# #     def get_chat_history(self):
# #         """Get chat history as a list."""
# #         if self.chat_history:
# #             return json.loads(self.chat_history)
# #         return []

# # # Create the database
# # with app.app_context():
# #     db.create_all()

# # # Load user function for Flask-Login
# # @login_manager.user_loader
# # def load_user(user_id):
# #     return User.query.get(int(user_id))

# # # Routes for user authentication
# # @app.route('/login', methods=['GET', 'POST'])
# # def login():
# #     if request.method == 'POST':
# #         username = request.form['username']
# #         password = request.form['password']
# #         user = User.query.filter_by(username=username).first()
        
# #         if user and check_password_hash(user.password, password):
# #             login_user(user)
# #             return redirect(url_for('index'))  # Redirect to homepage after login
# #         else:
# #             return "Invalid credentials, please try again.", 401
    
# #     return render_template('login.html')

# # @app.route('/signup', methods=['GET', 'POST'])
# # def signup():
# #     if request.method == 'POST':
# #         username = request.form['username']
# #         email = request.form['email']
# #         password = request.form['password']
# #         hashed_password = generate_password_hash(password, method='scrypt', salt_length=16)
        
# #         new_user = User(username=username, email=email, password=hashed_password)
# #         db.session.add(new_user)
# #         db.session.commit()
        
# #         return redirect(url_for('login'))
    
# #     return render_template('signup.html')

# # @app.route('/logout')
# # @login_required
# # def logout():
# #     logout_user()
# #     return redirect(url_for('login'))

# # # Profile route to view and update user details
# # @app.route('/profile', methods=['GET', 'POST'])
# # @login_required
# # def profile():
# #     if request.method == 'POST':
# #         # Update profile picture and preferences
# #         profile_picture = request.files.get('profile_picture')
# #         preferences = request.form.get('preferences')

# #         if profile_picture:
# #             # Save profile picture
# #             filename = secure_filename(profile_picture.filename)
# #             profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
# #             profile_picture.save(profile_picture_path)
# #             current_user.profile_picture = profile_picture_path

# #         if preferences:
# #             # Update preferences (e.g., language, theme)
# #             current_user.set_preferences(json.loads(preferences))

# #         db.session.commit()

# #         return redirect(url_for('profile'))  # Redirect to the profile page to show updates

# #     return render_template('profile.html', user=current_user)


# # # Function to classify user input using the ML model
# # def classify_intent(user_input):
# #     try:
# #         return model.predict([user_input])[0]
# #     except Exception as e:
# #         app.logger.error(f"Error classifying intent: {e}")
# #         return "unknown"

# # # Generate a response based on the intent
# # def generate_response(intent, user_input=None):
# #     if intent == "unknown" and user_input:
# #         # Search Google for the user input
# #         search_result = search_google(user_input)
# #         return search_result or responses["unknown"]
# #     return responses.get(intent, responses["unknown"])

# # # Search Google using the Custom Search API
# # def search_google(query):
# #     try:
# #         url = f"https://www.googleapis.com/customsearch/v1"
# #         params = {
# #             "key": GOOGLE_API_KEY,
# #             "cx": SEARCH_ENGINE_ID,
# #             "q": query,
# #         }
# #         response = requests.get(url, params=params)
# #         response.raise_for_status()
# #         data = response.json()

# #         # Extract the top search result
# #         if "items" in data:
# #             top_result = data["items"][0]
# #             title = top_result.get("title", "No title")
# #             snippet = top_result.get("snippet", "No description")
# #             link = top_result.get("link", "No link")
# #             return f"{title}\n{snippet}\nRead more: {link}"
# #         return "I couldn't find anything on that topic."
# #     except Exception as e:
# #         app.logger.error(f"Error fetching Google search results: {e}")
# #         return "An error occurred while searching online."


# # @app.route('/chat', methods=['POST'])
# # @login_required
# # def chat():
# #     try:
# #         if not request.is_json:
# #             return jsonify({'error': 'Invalid JSON format'}), 400

# #         user_input = request.json.get('message')
# #         if not user_input:
# #             return jsonify({'error': 'Message cannot be empty'}), 400

# #         # Classify intent using ML model
# #         intent = classify_intent(user_input)
        
# #         # Generate a response based on the intent
# #         response = generate_response(intent, user_input)

# #         # Update training data dynamically for unknown inputs
# #         if intent == "unknown":
# #             training_data.append((user_input, "unknown"))
# #             model.fit(*zip(*training_data))  # Retrain the model with updated data

# #         # Update chat history
# #         chat_history = current_user.get_chat_history()
# #         chat_history.append({'user': user_input, 'response': response})
# #         current_user.set_chat_history(chat_history)
# #         db.session.commit()

# #         app.logger.info(f"Intent: {intent}, Response: {response}")
# #         return jsonify({'response': response})

# #     except Exception as e:
# #         app.logger.error(f"Error processing chat request: {e}")
# #         return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500

# # # Lofi video generation route (authentication required)
# # @app.route('/generate_lofi', methods=['POST'])
# # @login_required
# # def generate_lofi_video():
# #     try:
# #         # Get uploaded files and form data
# #         image_file = request.files.get('image')
# #         audio_file = request.files.get('audio')
# #         width = int(request.form.get('width', 800))
# #         height = int(request.form.get('height', 600))

# #         if not image_file or not audio_file:
# #             return jsonify({'error': 'Image and audio files are required'}), 400

# #         # Save uploaded files
# #         image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
# #         audio_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
# #         image_file.save(image_path)
# #         audio_file.save(audio_path)

# #         # Generate lofi GIF and video (adjust function accordingly)
# #         gif_path, video_path = generate_lofi_gif(image_path, audio_path, width, height)

# #         return jsonify({
# #             'gif_url': f'/uploads/{os.path.basename(gif_path)}',
# #             'video_url': f'/uploads/{os.path.basename(video_path)}'
# #         })

# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500


# # @app.route('/generate_ai_video', methods=['POST'])
# # @login_required
# # def generate_ai_video():
# #     try:
# #         prompt = request.json.get('prompt')
# #         if not prompt:
# #             return jsonify({'error': 'Prompt is required'}), 400

# #         # Simulate video generation (Replace this with actual AI video generation logic)
# #         video_filename = f"generated_video_{current_user.id}.mp4"
# #         video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)

# #         # Simulated response
# #         return jsonify({
# #             'message': 'AI Video generated successfully!',
# #             'video_url': f'/uploads/{video_filename}'
# #         })

# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500



# # @app.route('/generate_ai_music', methods=['POST'])
# # @login_required
# # def generate_ai_music():
# #     try:
# #         mood = request.json.get('mood')
# #         if not mood:
# #             return jsonify({'error': 'Mood is required'}), 400

# #         # Simulate music generation (Replace this with actual AI music generation logic)
# #         music_filename = f"generated_music_{current_user.id}.mp3"
# #         music_path = os.path.join(app.config['UPLOAD_FOLDER'], music_filename)

# #         # Simulated response
# #         return jsonify({
# #             'message': 'AI Music generated successfully!',
# #             'music_url': f'/uploads/{music_filename}'
# #         })

# #     except Exception as e:
# #         return jsonify({'error': str(e)}), 500


# # @app.route('/')
# # @login_required
# # def index():
# #     return render_template('index.html')

# # # File upload route
# # @app.route('/uploads/<filename>')
# # def uploaded_file(filename):
# #     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# # if __name__ == '__main__':
# #     app.run(debug=True)



# import os
# import re
# import json
# import requests
# from datetime import datetime
# from dotenv import load_dotenv
# from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
# from flask_wtf.csrf import CSRFProtect
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from flask_talisman import Talisman
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.pipeline import make_pipeline

# # Load environment variables
# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)
# app.config.update({
#     'SECRET_KEY': os.environ.get('SECRET_KEY'),
#     'SQLALCHEMY_DATABASE_URI': f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'users.db')}",
#     'SQLALCHEMY_TRACK_MODIFICATIONS': False,
#     'UPLOAD_FOLDER': 'uploads',
#     'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
#     'SEARCH_ENGINE_ID': os.environ.get('SEARCH_ENGINE_ID'),
#     'MAX_CONTENT_LENGTH': 10 * 1024 * 1024  # 10MB
# })

# # Security extensions
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

# # Initialize database
# db = SQLAlchemy(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

# # File upload constraints
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # --- Database Models ---
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     profile_picture = db.Column(db.String(120))
#     preferences = db.Column(db.Text)
#     chat_history = db.Column(db.Text)

#     def set_preferences(self, preferences_dict):
#         self.preferences = json.dumps(preferences_dict)

#     def get_preferences(self):
#         return json.loads(self.preferences) if self.preferences else {}

#     def set_chat_history(self, chat_history_list):
#         self.chat_history = json.dumps(chat_history_list)

#     def get_chat_history(self):
#         return json.loads(self.chat_history) if self.chat_history else []

# # Create tables
# with app.app_context():
#     db.create_all()

# # --- ML Model Setup ---
# training_data = [
#     ("hello", "greeting"), ("hi", "greeting"),
#     ("bye", "farewell"), ("thanks", "thanks"),
#     ("help", "help"), ("joke", "joke")
# ]

# responses = {
#     "greeting": "Hello! How can I assist you?",
#     "farewell": "Goodbye! Have a great day!",
#     "thanks": "You're welcome!",
#     "help": "How can I help?",
#     "joke": "Why did the computer go to therapy? It had too many bytes of emotional baggage!",
#     "unknown": "I'm not sure how to respond to that."
# }

# texts, labels = zip(*training_data)
# model = make_pipeline(TfidfVectorizer(), MultinomialNB())
# model.fit(texts, labels)

# # --- Authentication Routes ---
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# @app.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         user = User.query.filter_by(username=username).first()
        
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('index'))
#         return "Invalid credentials", 401
#     return render_template('login.html')

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')

#         if not is_password_complex(password):
#             return "Password must be 8+ chars with uppercase, lowercase, and numbers", 400

#         hashed_pw = generate_password_hash(password, method='scrypt')
#         new_user = User(username=username, email=email, password=hashed_pw)
        
#         db.session.add(new_user)
#         try:
#             db.session.commit()
#         except:
#             db.session.rollback()
#             return "Username/email already exists", 400
            
#         return redirect(url_for('login'))
#     return render_template('signup.html')

# def is_password_complex(password):
#     return (len(password) >= 8 and 
#             re.search(r"\d", password) and 
#             re.search(r"[A-Z]", password) and 
#             re.search(r"[a-z]", password))

# # --- Core Application Routes ---
# @app.route('/')
# @login_required
# def index():
#     return render_template('index.html')

# @app.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     if request.method == 'POST':
#         # Handle file upload
#         if 'profile_picture' in request.files:
#             file = request.files['profile_picture']
#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 current_user.profile_picture = filename

#         # Handle preferences
#         if 'preferences' in request.form:
#             try:
#                 prefs = json.loads(request.form['preferences'])
#                 current_user.set_preferences(prefs)
#             except json.JSONDecodeError:
#                 return "Invalid preferences format", 400

#         db.session.commit()
#         return redirect(url_for('profile'))
    
#     return render_template('profile.html', user=current_user)

# @app.route('/chat', methods=['POST'])
# @login_required
# def chat():
#     try:
#         data = request.get_json()
#         if not data or 'message' not in data:
#             return jsonify({'error': 'Invalid request'}), 400

#         user_input = data['message']
#         intent = model.predict([user_input])[0]
#         response = responses.get(intent, responses['unknown'])

#         # Update chat history
#         history = current_user.get_chat_history()
#         history.append({'user': user_input, 'response': response, 'timestamp': str(datetime.now())})
#         current_user.set_chat_history(history)
#         db.session.commit()

#         return jsonify({'response': response})

#     except Exception as e:
#         app.logger.error(f"Chat error: {str(e)}")
#         return jsonify({'error': 'Processing error'}), 500

# # --- File Handling ---
# @app.route('/uploads/<filename>')
# @login_required
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# # --- Error Handlers ---
# @app.errorhandler(404)
# def not_found(e):
#     return render_template('404.html'), 404

# @app.errorhandler(500)
# def server_error(e):
#     db.session.rollback()
#     return render_template('500.html'), 500

# # --- Production Setup ---
# if __name__ == '__main__':
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
#     if os.environ.get('FLASK_ENV') == 'production':
#         from waitress import serve
#         serve(app, host="0.0.0.0", port=5000)
#     else:
#         app.run(debug=False)
