from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder="frontend")
CORS(app)

# Initialize SQLite database
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        conn.commit()

init_db()

# Serve the index.html file
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        return jsonify([{"id": row[0], "description": row[1], "completed": bool(row[2])} for row in tasks])

# Add a new task
@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    description = data.get("description")
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
        conn.commit()
        task_id = cursor.lastrowid
    return jsonify({"id": task_id})

# Update a task (mark as completed/incomplete)
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    completed = data.get("completed")
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
        conn.commit()
    return jsonify({"message": "Task updated"})

# Delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return jsonify({"message": "Task deleted"})

if __name__ == "__main__":
    app.run(debug=True)