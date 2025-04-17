from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import smtplib
import dotenv

# Initialize
dotenv.load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_ADD')  # educationsports7@gmail.com
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')    # App password (16-char)
#app.config['MAIL_USERNAME'] = 'educationsports7@gmail.com'
#app.config['MAIL_PASSWORD'] = 'jturzqljlaraggdc'
# Initialize Flask-Mail AFTER config
mail = Mail(app)

# Debugging environment variable loading
print("EMAIL:", os.getenv('EMAIL_ADD'))
print("PASSWORD:", os.getenv('PASSWORD'))

# ===== Debugging SMTP =====
print("[DEBUG] SMTP Config:")
print(f"Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
print(f"TLS/SSL: TLS={app.config['MAIL_USE_TLS']}, SSL={app.config['MAIL_USE_SSL']}")
print(f"Email: {app.config['MAIL_USERNAME']}")
print(f"Password loaded: {bool(app.config['MAIL_PASSWORD'])}")  # True if password exists


# File Uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Authentication
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
def portfolio():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Login required for uploads', 'warning')
            return redirect(url_for('login'))
        
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('portfolio'))
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('portfolio'))
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'{filename} uploaded successfully!', 'success')
        else:
            flash('Allowed file types: PDF, DOCX, PPTX, JPG, PNG', 'danger')
            
        return redirect(url_for('portfolio'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('portfolio.html', files=files)

@app.route('/philosophy')
def philosophy():
    return render_template('philosophy.html')

@app.route('/reflect')
def reflect():
    return render_template('reflection.html')

# ===== Contact Route =====
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            print(f"\n[DEBUG] Trying to send email from {email}...")

            # In the contact route:
            msg = Message(
                subject=f"New Message from {name}",
                sender=email,  # From the form (e.g., user@example.com)
                recipients=[app.config['MAIL_USERNAME']],  # To your Gmail
                body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

            mail.send(msg)
            print("[DEBUG] ✅ Email sent successfully!")
            flash('Your message was sent!', 'success')

        except Exception as e:
            print(f"[DEBUG] ❌ SMTP Error: {str(e)}")
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

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'{filename} deleted successfully!', 'info')
    else:
        flash('File not found', 'danger')
    return redirect(url_for('portfolio'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)