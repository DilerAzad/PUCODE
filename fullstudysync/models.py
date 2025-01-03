from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    notes = db.relationship('Note', backref='video', cascade="all, delete", lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.String(10), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)