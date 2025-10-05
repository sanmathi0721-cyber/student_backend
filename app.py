from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import date

app = Flask(__name__)
CORS(app)

DB = "attendance.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cur = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login successful", "role": user["role"], "user_id": user["id"]})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db()
    cur = conn.execute("SELECT * FROM students")
    students = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(students)


@app.route('/mark', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    student_id = data.get('student_id')
    status = data.get('status', 'Present')
    today = date.today().isoformat()

    conn = get_db()
    conn.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                 (student_id, today, status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance marked successfully"})


@app.route('/view/<int:student_id>', methods=['GET'])
def view_attendance(student_id):
    conn = get_db()
    cur = conn.execute("SELECT * FROM attendance WHERE student_id=?", (student_id,))
    records = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(records)


if __name__ == '__main__':
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT, password TEXT, role TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, roll_no TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER, date TEXT, status TEXT)''')
    conn.commit()

    # Add default data
    cur = conn.execute("SELECT COUNT(*) as count FROM users")
    if cur.fetchone()["count"] == 0:
        conn.execute("INSERT INTO users (username, password, role) VALUES ('teacher','123','teacher')")
        conn.execute("INSERT INTO users (username, password, role) VALUES ('student','123','student')")
        conn.execute("INSERT INTO students (name, roll_no) VALUES ('John Doe','101')")
        conn.execute("INSERT INTO students (name, roll_no) VALUES ('Jane Doe','102')")
        conn.commit()

    conn.close()
    app.run(host='0.0.0.0', port=5000, debug=True)
