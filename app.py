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
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not is_password_complex(password):
            return "Password must be 8+ chars with uppercase, lowercase, and numbers", 400

        hashed_pw = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, email=email, password=hashed_pw)
        
        db.session.add(new_user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return "Username/email already exists", 400
            
        return redirect(url_for('login'))
    return render_template('signup.html')

def is_password_complex(password):
    return (len(password) >= 8 and 
            re.search(r"\d", password) and 
            re.search(r"[A-Z]", password) and 
            re.search(r"[a-z]", password))

# --- Core Application Routes ---
@app.route('/')
@login_required
def index():
    return render_template('index.html')

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


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid request'}), 400

        user_input = data['message']
        intent = model.predict([user_input])[0]
        response = responses.get(intent, responses['unknown'])

        # Update chat history
        history = current_user.get_chat_history()
        history.append({'user': user_input, 'response': response, 'timestamp': str(datetime.now())})
        current_user.set_chat_history(history)
        db.session.commit()

        return jsonify({'response': response})

    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Processing error'}), 500

# --- Lofi Video Generation Route ---
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
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

# --- Production Setup ---
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    if os.environ.get('FLASK_ENV') == 'production':
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(debug=True)
