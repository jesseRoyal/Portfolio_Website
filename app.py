from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = 'supersecret'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use the appropriate mail server (this is for Gmail)
app.config['MAIL_PORT'] = 465  # Port for SSL
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'jesse.nelson432@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'Jamesbond_456'  # Replace with your email password or app-specific password
app.config['MAIL_DEFAULT_SENDER'] = 'jesse.nelson432@gmail.com'  # Your email address
mail = Mail(app)

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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if name and email and message:
            # Send email using Flask-Mail
            msg = Message(f"New Message from {name}",
                          recipients=["jesse.nelson432@gmail.com"],  # Replace with your email
                          body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")
            try:
                mail.send(msg)
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
                flash('There was an issue sending your message. Please try again.', 'danger')
        else:
            flash('Please fill out all fields.', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/google-classroom')
def google_classroom():
    return redirect("https://classroom.google.com/c/Njk4NjQxNDI0Nzg4?cjc=v2b56cue")

if __name__ == '__main__':
    app.run(debug=True)
