from flask import Flask, render_template, request, redirect, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)

# Define the model
class MeetingNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    attendees = db.Column(db.Text)
    agenda = db.Column(db.Text)
    decisions = db.Column(db.Text)
    actions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database (if not already exists)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/submit', methods=['POST'])
def submit():
    new_note = MeetingNote(
        date=request.form['date'],
        attendees=request.form['attendees'],
        agenda=request.form['agenda'],
        decisions=request.form['decisions'],
        actions=request.form['actions']
    )
    db.session.add(new_note)
    db.session.commit()
    return redirect('/notes')

@app.route('/notes')
def notes():
    all_notes = MeetingNote.query.order_by(MeetingNote.created_at.desc()).all()
    return render_template('notes.html', notes=all_notes)

@app.route('/download/<int:note_id>')
def download_pdf(note_id):
    note = MeetingNote.query.get_or_404(note_id)

    pdf_path = f"static/note_{note_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 50  # Top margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Meeting Note")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Date: {note.date}")
    y -= 20
    c.drawString(50, y, f"Attendees: {note.attendees}")
    y -= 20

    c.drawString(50, y, "Agenda:")
    y -= 20
    for line in note.agenda.split('\n'):
        c.drawString(70, y, line)
        y -= 15

    y -= 10
    c.drawString(50, y, "Decisions:")
    y -= 20
    for line in note.decisions.split('\n'):
        c.drawString(70, y, line)
        y -= 15

    y -= 10
    c.drawString(50, y, "Action Items:")
    y -= 20
    for line in note.actions.split('\n'):
        c.drawString(70, y, line)
        y -= 15

    c.save()
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5000)



