from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    with sqlite3.connect("calendar.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                note TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# Serve frontend
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/notes", methods=["GET"])
def get_notes():
    year = request.args.get("year")
    month = request.args.get("month")

    if not (year and month):
        return jsonify({"error": "Year and month are required"}), 400

    with sqlite3.connect("calendar.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, note FROM notes WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?", (year, month))
        notes = cursor.fetchall()

    return jsonify([{"id": row[0], "date": row[1], "note": row[2]} for row in notes])

@app.route("/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    date = data.get("date")
    note = data.get("note")

    if not (date and note):
        return jsonify({"error": "Date and note are required"}), 400

    with sqlite3.connect("calendar.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (date, note) VALUES (?, ?)", (date, note))
        conn.commit()
        note_id = cursor.lastrowid

    return jsonify({"id": note_id, "date": date, "note": note})

@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with sqlite3.connect("calendar.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    return jsonify({"message": "Note deleted"})

if __name__ == "__main__":
    app.run(debug=True)