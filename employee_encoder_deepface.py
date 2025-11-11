import os
import numpy as np
import json
from deepface import DeepFace
import mysql.connector

EMPLOYEE_FOLDER = "employee_data"

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="!manish!", 
    database="powergrid_face_db"
)
cursor = conn.cursor()

employee_count = 0

for folder in os.listdir(EMPLOYEE_FOLDER):
    folder_path = os.path.join(EMPLOYEE_FOLDER, folder)
    if not os.path.isdir(folder_path):
        continue

    metadata_path = os.path.join(folder_path, "metadata.txt")
    if not os.path.exists(metadata_path):
        print(f"[⚠️] Skipping {folder}, no metadata.txt found")
        continue

    # Read metadata
    metadata = {}
    with open(metadata_path, "r") as f:
        for line in f:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                metadata[key.strip().lower()] = value.strip()

    employee_id = metadata.get("employee id")
    name = metadata.get("name", "Unknown")
    email = metadata.get("email", "Unknown")

    if not employee_id:
        print(f"[⚠️] No Employee ID in metadata for {folder}")
        continue

    embeddings = []

    for file in os.listdir(folder_path):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder_path, file)
            try:
                embedding_obj = DeepFace.represent(
                    img_path=img_path,
                    model_name="ArcFace",
                    enforce_detection=False
                )[0]
                embeddings.append(embedding_obj["embedding"])
                print(f"[+] Encoded {name} - {file}")
            except Exception as e:
                print(f"[❌] Failed to encode {file}: {e}")

    if embeddings:
        avg_embedding = np.mean(embeddings, axis=0).tolist()
        embedding_json = json.dumps(avg_embedding)

        # Insert or update if employee already exists
        cursor.execute(
            """
            INSERT INTO employees (employee_id, name, email, embedding)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                email = VALUES(email),
                embedding = VALUES(embedding),
                updated_at = CURRENT_TIMESTAMP
            """,
            (employee_id, name, email, embedding_json),
        )

        conn.commit()
        employee_count += 1

conn.close()

print(f"[✅] Saved {employee_count} employees to MySQL database.")
