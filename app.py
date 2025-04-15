from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mail import Mail, Message
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)

app.secret_key = 'supersecret'

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

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('portfolio'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('portfolio.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'{filename} deleted successfully.', 'info')
    else:
        flash(f'{filename} not found.', 'danger')
    return redirect(url_for('portfolio'))

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

@app.route('/google-classroom')
def google_classroom():
    return redirect("https://classroom.google.com/c/Njk4NjQxNDI0Nzg4?cjc=v2b56cue")

if __name__ == '__main__':
    app.run(debug=True)
