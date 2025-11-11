from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import shutil
import mysql.connector
import json
from scipy.spatial.distance import cosine
import zipfile
import io
import csv
from flask import Response

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="!manish!",
        database="powergrid_face_db",
        buffered=True  
    )

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emp_id = request.form["employee_id"].strip()
        password = request.form["password"].strip()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE employee_id = %s AND password = %s", (emp_id, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["employee_id"] = emp_id
            return redirect(url_for("events"))
        else:
            return render_template("index.html", error="Invalid credentials.")
    return render_template("index.html")

@app.route("/events")
def events():
    if "employee_id" not in session:
        return redirect(url_for("login"))

    emp_id = session["employee_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (emp_id,))
    employee = cursor.fetchone()
    if not employee:
        return render_template("events.html", employee={"name": "Unknown", "email": "Unknown", "employee_id": emp_id}, events=[])

    emp_embedding = json.loads(employee["embedding"])
    matched_event_ids = []
    seen_event_ids = set()

    cursor.execute("""
        SELECT mp.id, mp.embedding, mp.event_id, e.event_name, e.metadata AS event_metadata
        FROM matched_photos mp
        JOIN events e ON mp.event_id = e.id
    """)
    results = cursor.fetchall()

    for row in results:
        if not row["embedding"]:
            continue
        try:
            photo_embedding = json.loads(row["embedding"])
            distance = cosine(emp_embedding, photo_embedding)
            if distance < 0.55:
                if row["event_id"] not in seen_event_ids:
                    seen_event_ids.add(row["event_id"])
                    metadata_dict = json.loads(row.get("event_metadata", "{}"))
                    matched_event_ids.append((row["event_id"], row["event_name"], metadata_dict))
                cursor.execute("""
                    UPDATE matched_photos SET employee_id = %s, similarity_score = %s WHERE id = %s
                """, (emp_id, round(1 - distance, 4), row["id"]))
        except Exception as e:
            print("[Error in cosine]", e)

    conn.commit()
    cursor.close()
    conn.close()

    sorted_events = sorted(
        matched_event_ids,
        key=lambda item: item[2].get("date", ""),
        reverse=True
    )

    return render_template("events.html", employee=employee, events=[(e[1], e[2]) for e in sorted_events])

@app.route("/event/<event_name>")
def event_photos(event_name):
    if "employee_id" not in session:
        return redirect(url_for("login"))

    emp_id = session["employee_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (emp_id,))
    employee = cursor.fetchone()
    if not employee:
        return render_template("profile.html", employee={"name": "Unknown", "email": "Unknown", "employee_id": emp_id}, photos=[])

    emp_embedding = json.loads(employee["embedding"])
    photo_map = {}

    cursor.execute("""
        SELECT mp.*, e.event_name, e.metadata AS event_metadata
        FROM matched_photos mp
        JOIN events e ON mp.event_id = e.id
        WHERE e.event_name = %s
    """, (event_name,))
    results = cursor.fetchall()

    for entry in results:
        try:
            if not entry["embedding"]:
                continue

            photo_path = entry["photo_path"]
            photo_embedding = json.loads(entry["embedding"])
            distance = cosine(emp_embedding, photo_embedding)

            if distance < 0.55:
                if photo_path not in photo_map:
                    filename = os.path.basename(photo_path)
                    static_path = os.path.join("static", "matched_photos", filename)
                    if not os.path.exists(static_path):
                        shutil.copy(photo_path, static_path)

                    metadata = json.loads(entry.get("event_metadata", "{}"))
                    photo_map[photo_path] = {
                        "filename": filename,
                        "event_name": entry.get("event_name", "Unknown"),
                        "event_place": metadata.get("event place", metadata.get("venue", "Unknown")),
                        "event_date": metadata.get("event date", metadata.get("date", "Unknown")),
                        "geolocation": metadata.get("geolocation", None),
                        "employee_ids": set(),
                        "similarity_scores": []
                    }

                photo_map[photo_path]["employee_ids"].add(emp_id)
                photo_map[photo_path]["similarity_scores"].append(round(1 - distance, 4))

                cursor.execute("""
                    UPDATE matched_photos SET employee_id = %s, similarity_score = %s WHERE id = %s
                """, (emp_id, round(1 - distance, 4), entry["id"]))

        except Exception as e:
            print("[Error in /event route]", e)

    conn.commit()
    cursor.close()
    conn.close()

    # Convert employee_id sets to sorted lists for template compatibility
    matches = []
    for photo in photo_map.values():
        photo["employee_ids"] = sorted(photo["employee_ids"])
        matches.append(photo)

    return render_template("profile.html", employee=employee, photos=matches)

@app.route("/download/<event_name>")
def download_event_photos(event_name):
    if "employee_id" not in session:
        return redirect(url_for("login"))

    emp_id = session["employee_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (emp_id,))
    employee = cursor.fetchone()
    if not employee:
        return "No employee found", 404

    emp_embedding = json.loads(employee["embedding"])
    matched_files = []

    cursor.execute("""
        SELECT mp.*, e.event_name
        FROM matched_photos mp
        JOIN events e ON mp.event_id = e.id
        WHERE e.event_name = %s
    """, (event_name,))
    results = cursor.fetchall()

    for entry in results:
        try:
            if not entry["embedding"]:
                continue
            photo_embedding = json.loads(entry["embedding"])
            distance = cosine(emp_embedding, photo_embedding)
            if distance < 0.55:
                matched_files.append(entry["photo_path"])
        except:
            continue

    cursor.close()
    conn.close()

    if not matched_files:
        return "No matched photos found", 404

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for file_path in matched_files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{event_name}_matched_photos.zip"
    )

@app.route("/download_csv/<event_name>")
def download_csv(event_name):
    if "employee_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all matched_photos for the given event
    cursor.execute("""
        SELECT mp.photo_path, mp.employee_id, mp.similarity_score, e.event_name, e.metadata AS event_metadata
        FROM matched_photos mp
        JOIN events e ON mp.event_id = e.id
        WHERE e.event_name = %s AND mp.employee_id IS NOT NULL
    """, (event_name,))
    results = cursor.fetchall()

    # Group by photo_path
    photo_groups = {}
    for entry in results:
        photo_path = entry["photo_path"]
        emp_id = str(entry["employee_id"])
        score = entry["similarity_score"]

        if photo_path not in photo_groups:
            photo_groups[photo_path] = {
                "event_name": entry["event_name"],
                "employee_ids": set(),
                "similarity_scores": [],
                "metadata": json.loads(entry.get("event_metadata", "{}"))
            }

        photo_groups[photo_path]["employee_ids"].add(emp_id)
        if score is not None:
            photo_groups[photo_path]["similarity_scores"].append(score)

    # Prepare CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Photo Filename", "Event Name", "Employee IDs", "Avg Similarity Score", "Event Date", "Event Place", "Geolocation"])

    for photo_path, data in photo_groups.items():
        filename = os.path.basename(photo_path)
        employee_ids = ", ".join(sorted(data["employee_ids"]))
        scores = data["similarity_scores"]
        avg_score = round(sum(scores) / len(scores), 4) if scores else "N/A"

        meta = data["metadata"]
        writer.writerow([
            filename,
            data["event_name"],
            employee_ids,
            avg_score,
            meta.get("event date", meta.get("date", "Unknown")),
            meta.get("event place", meta.get("venue", "Unknown")),
            meta.get("geolocation", "")
        ])

    cursor.close()
    conn.close()

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={event_name}_matched_photos.csv"}
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    os.makedirs("static/matched_photos", exist_ok=True)
    app.run(debug=True)