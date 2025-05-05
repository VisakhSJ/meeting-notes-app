from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to something more secure

# Setup SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meeting_notes.db'
db = SQLAlchemy(app)

# Define a database model
class MeetingNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)

# ✅ List of allowed email IDs
ALLOWED_EMAILS = [
    "Vinod.Vijayan@gds.ey.com",
    "Ayishath.Rifa@gds.ey.com",
    "Visakh.S.J@gds.ey.com"
]

# Home page - show form if logged in
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    notes = MeetingNote.query.all()
    return render_template('home.html', notes=notes)

# Save note
@app.route('/save', methods=['POST'])
def save():
    if 'user' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    content = request.form['content']
    note = MeetingNote(title=title, content=content)
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('home'))

# Download note as PDF
@app.route('/download/<int:note_id>')
def download(note_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    note = MeetingNote.query.get_or_404(note_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 14)
    p.drawString(100, 750, f"Title: {note.title}")
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, "Content:")
    y = 700
    for line in note.content.split('\n'):
        p.drawString(100, y, line)
        y -= 20
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{note.title}.pdf", mimetype='application/pdf')

# Common password
COMMON_PASSWORD = "pass123"

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in ALLOWED_EMAILS and password == COMMON_PASSWORD:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)





