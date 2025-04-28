# Import necessary libraries
from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory, flash
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import os
import smtplib
import dotenv
import json
import requests
import logging
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Load environment variables
dotenv.load_dotenv()

# Initialize CSRF protection FIRST
csrf = CSRFProtect(app)

# In-memory session storage for chatbot
sessions = {}

# Secret key for sessions and CSRF
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# ================== Flask-Mail Configuration ==================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_ADD')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
mail = Mail(app)

# ================== File Upload Configuration ==================
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================== Authentication Setup ==================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to 'login' page if not authenticated

# Admin credentials stored securely
ADMIN_CREDS = {
    os.getenv('ADMIN_USERNAME', 'admin'): generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123'))
}

# Simple User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ================== Helper Functions ==================

# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load file descriptions
def load_descriptions():
    desc_file = os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions.json')
    if os.path.exists(desc_file):
        with open(desc_file) as f:
            return json.load(f)
    return {}

# Save file descriptions
def save_descriptions(descriptions):
    desc_file = os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions.json')
    with open(desc_file, 'w') as f:
        json.dump(descriptions, f)

# ================== Routes ==================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio', methods=['GET', 'POST'])
#@login_required  # Uncomment if you want only logged-in users to upload
def portfolio():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('portfolio'))
        
        file = request.files['file']
        description = request.form.get('description', '')

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('portfolio'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Save description
            descriptions = load_descriptions()
            descriptions[filename] = description
            save_descriptions(descriptions)

            flash(f'{filename} uploaded successfully!', 'success')
        else:
            flash('Allowed file types: PDF, DOCX, PPTX, JPG, PNG', 'danger')
            
        return redirect(url_for('portfolio'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files = [f for f in files if f != 'descriptions.json']
    descriptions = load_descriptions()

    return render_template('portfolio.html', files=files, descriptions=descriptions)

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    try:
        # Check CSRF token
        if not request.form.get('csrf_token'):
            flash('Invalid request: CSRF token missing', 'danger')
            return redirect(url_for('portfolio'))

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(file_path):
            flash('File not found', 'danger')
            return redirect(url_for('portfolio'))

        os.remove(file_path)

        # Update descriptions
        descriptions = load_descriptions()
        if filename in descriptions:
            del descriptions[filename]
            save_descriptions(descriptions)

        flash(f'{filename} deleted successfully', 'success')

    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'danger')
        app.logger.error(f'Delete error: {e}')

    return redirect(url_for('portfolio'))

@app.route('/philosophy')
def philosophy():
    return render_template('philosophy.html')

@app.route('/reflect')
def reflect():
    return render_template('reflection.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            msg = Message(
                subject=f"New Message from {name}",
                sender=email,
                recipients=[app.config['MAIL_USERNAME']],
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            )
            mail.send(msg)
            flash('Your message was sent!', 'success')

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in ADMIN_CREDS and check_password_hash(ADMIN_CREDS[username], password):
            user = User(username)
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('portfolio'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/google-classroom')
def google_classroom():
    return redirect("https://classroom.google.com")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/test-delete', methods=['GET', 'POST'])
def test_delete():
    if request.method == 'POST':
        print("Delete form submitted!")
        return "Delete action received!"

# Route that the chatbot frontend talks to
@app.route('/api/chatbot', methods=['POST'])
@csrf.exempt
def chatbot_reply():
    data = request.get_json()

    print("Received message:", data)

    # Extract user's message
    user_message = data.get('message')
    if not user_message:
        print("Error: No message provided.")
        return jsonify({'success': False, 'reply': 'No message provided.'}), 400

    # Prepare the new API call
    url = "https://chatgpt-42.p.rapidapi.com/chat"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "model": "gpt-4o-mini"
    }
    headers = {
        "x-rapidapi-key": "ba0b853dc8mshed2be5e2cf6966bp1aaf49jsn78c335d4e373",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        # Send request to the new API
        print("Sending request to API:", url)
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        api_data = response.json()
        print("Received API response:", api_data)

        # Get the reply text from API response
        bot_reply = api_data['choices'][0]['message']['content']

        print("Returning reply:", bot_reply)
        return jsonify({'success': True, 'reply': bot_reply})

    except Exception as e:
        print('Error talking to API:', e)
        return jsonify({'success': False, 'reply': '⚠️ Sorry, there was an error processing your request.'}), 500

if __name__ == "__main__":
    app.run(debug=True)

