from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize SQLite database
def init_db():
    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# Serve the frontend
@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

# Upload a PDF
@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith(".pdf"):
        filename = file.filename
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        # Save file info to the database
        with sqlite3.connect("books.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (filename, filepath) VALUES (?, ?)", (filename, filepath))
            conn.commit()
            book_id = cursor.lastrowid
        return jsonify({"id": book_id, "filename": filename, "filepath": filepath})
    return jsonify({"error": "Invalid file format"}), 400

# Get all uploaded PDFs
@app.route("/books", methods=["GET"])
def get_books():
    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        return jsonify([{"id": row[0], "filename": row[1], "filepath": row[2]} for row in books])

# Delete a PDF by ID
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_pdf(book_id):
    with sqlite3.connect("books.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filepath FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if book:
            os.remove(book[0])  # Delete file from the filesystem
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            return jsonify({"message": "Book deleted"})
        return jsonify({"error": "Book not found"}), 404

# Serve uploaded PDFs
@app.route("/uploads/<path:filename>", methods=["GET"])
def download_pdf(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)