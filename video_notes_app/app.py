from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, Video, Note

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Database initialization
@app.before_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/videos", methods=["GET", "POST"])
def manage_videos():
    if request.method == "POST":
        data = request.json
        video_id = data["url"].split("v=")[-1].split("&")[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"

        video = Video(url=embed_url)
        db.session.add(video)
        db.session.commit()

        return jsonify({"id": video.id, "url": video.url, "notes": []}), 201

    videos = Video.query.all()
    response = [
        {
            "id": video.id,
            "url": video.url,
            "notes": [{"id": note.id, "text": note.text, "time": note.timestamp} for note in video.notes],
        }
        for video in videos
    ]
    return jsonify(response)

@app.route("/api/videos/<int:video_id>", methods=["DELETE"])
def delete_video(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    db.session.delete(video)
    db.session.commit()
    return jsonify({"message": "Video deleted"}), 200

@app.route("/api/videos/<int:video_id>/notes", methods=["POST"])
def add_note(video_id):
    video = Video.query.get(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    data = request.json
    note = Note(text=data["note"], timestamp=data["time"], video=video)
    db.session.add(note)
    db.session.commit()

    return jsonify({"id": note.id, "text": note.text, "time": note.timestamp}), 201

@app.route("/api/videos/<int:video_id>/notes/<int:note_id>", methods=["DELETE"])
def delete_note(video_id, note_id):
    note = Note.query.filter_by(id=note_id, video_id=video_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)