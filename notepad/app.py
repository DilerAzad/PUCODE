from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder="frontend")
CORS(app)

# Initialize SQLite database
def init_db():
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# Route to serve the index.html
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Route to get all notes
@app.route("/notes", methods=["GET"])
def get_notes():
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()
        return jsonify([{"id": row[0], "title": row[1], "content": row[2]} for row in notes])

# Route to get a single note by ID
@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note_by_id(note_id):
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        if note:
            return jsonify({"id": note[0], "title": note[1], "content": note[2]})
        return jsonify({"error": "Note not found"}), 404

# Route to add a new note
@app.route("/notes", methods=["POST"])
def add_note():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        note_id = cursor.lastrowid
    return jsonify({"id": note_id})

# Route to delete a note by ID
@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note_by_id(note_id):
    with sqlite3.connect("notes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return jsonify({"message": "Note deleted"})

if __name__ == "__main__":
    app.run(debug=True)