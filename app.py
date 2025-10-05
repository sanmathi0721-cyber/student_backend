from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Attendance

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ---------- ROUTES ----------
@app.route("/")
def home():
    return jsonify({"message": "Backend is running!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"], password=data["password"]).first()
    if user:
        return jsonify({"username": user.username, "role": user.role})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/attendance/mark", methods=["POST"])
def mark_attendance():
    data = request.get_json()
    username = data.get("username")
    status = data.get("status")

    if not username or not status:
        return jsonify({"error": "Missing data"}), 400

    attendance = Attendance(username=username, status=status)
    db.session.add(attendance)
    db.session.commit()

    return jsonify({"message": "Attendance marked successfully"})


@app.route("/attendance/view/<username>", methods=["GET"])
def view_attendance(username):
    records = Attendance.query.filter_by(username=username).all()
    result = [{"id": a.id, "username": a.username, "status": a.status, "date": a.date} for a in records]
    return jsonify(result)


@app.route("/attendance/export", methods=["GET"])
def export_attendance():
    import csv
    from io import StringIO
    records = Attendance.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Username", "Status", "Date"])
    for r in records:
        writer.writerow([r.id, r.username, r.status, r.date])
    return output.getvalue(), 200, {"Content-Type": "text/csv"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Add default users if not exists
        if not User.query.first():
            teacher = User(username="teacher", password="123", role="teacher")
            student = User(username="student", password="123", role="student")
            db.session.add_all([teacher, student])
            db.session.commit()
    app.run(host="0.0.0.0", port=5000, debug=True)
