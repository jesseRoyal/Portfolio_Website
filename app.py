from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import os
import smtplib
import dotenv
import json

# Initialize environment variables
dotenv.load_dotenv()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize CSRF protection FIRST
csrf = CSRFProtect(app)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_ADD')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
mail = Mail(app)

# File Uploads Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Authentication Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ADMIN_CREDS = {
    os.getenv('ADMIN_USERNAME', 'admin'): 
    generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123'))
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ============= ROUTES =============
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio', methods=['GET', 'POST'])
#@login_required
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
        # Verify CSRF token
        if not request.form.get('csrf_token'):
            flash('Invalid request: CSRF token missing', 'danger')
            return redirect(url_for('portfolio'))
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            flash('File not found', 'danger')
            return redirect(url_for('portfolio'))

        # Delete file
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

# Helper functions
def load_descriptions():
    desc_file = os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions.json')
    if os.path.exists(desc_file):
        with open(desc_file) as f:
            return json.load(f)
    return {}

def save_descriptions(descriptions):
    desc_file = os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions.json')
    with open(desc_file, 'w') as f:
        json.dump(descriptions, f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Other routes remain unchanged...
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
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")
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
        print("Delete form submitted!")  # Check if this appears in terminal
        return "Delete action received!"  # Simple response

if __name__ == '__main__':
    app.run(debug=True)