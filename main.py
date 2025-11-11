import os
import mysql.connector
import json
from deepface import DeepFace
from tqdm import tqdm
from multiprocessing import Pool
import multiprocessing

EVENT_FOLDER = "event_data"

def read_metadata_txt(path):
    metadata = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    metadata[key.strip().lower()] = value.strip()
    return metadata

def process_image(args):
    import cv2
    img_path, event_id = args
    try:
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("Image can't be read (might be corrupted or empty)")

        max_dim = max(img.shape[:2])
        if max_dim > 3000:
            scale = 3000 / max_dim
            new_dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
            img = cv2.resize(img, new_dim)
            temp_path = img_path + "_resized.jpg"
            cv2.imwrite(temp_path, img)
            img_path_to_use = temp_path
        else:
            img_path_to_use = img_path

        embedding_obj = DeepFace.represent(
            img_path=img_path_to_use,
            model_name="ArcFace",
            enforce_detection=False
        )

        conn_local = mysql.connector.connect(
            host="localhost",
            user="root",
            password="!manish!",
            database="powergrid_face_db"
        )
        cursor_local = conn_local.cursor()

        for face in embedding_obj:
            embedding_json = json.dumps(face["embedding"])
            cursor_local.execute("""
                INSERT INTO matched_photos (employee_id, event_id, photo_path, similarity_score, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (None, event_id, img_path, None, embedding_json))
            conn_local.commit()

        conn_local.close()

        if img_path_to_use != img_path and os.path.exists(img_path_to_use):
            os.remove(img_path_to_use)

        return True

    except Exception as e:
        print(f"[❌] Failed on image {os.path.basename(img_path)}: {e}")
        return False

def main():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="!manish!",
        database="powergrid_face_db"
    )
    cursor = conn.cursor()

    print("[⚙️] Rebuilding event face database into MySQL...")
    total_faces = 0
    event_count = 0

    for event_name in os.listdir(EVENT_FOLDER):
        event_path = os.path.join(EVENT_FOLDER, event_name)
        if not os.path.isdir(event_path):
            print(f"[⏭️] Skipping {event_name} because it's not a directory")
            continue

        metadata_path = os.path.join(event_path, "metadata.txt")
        if not os.path.exists(metadata_path):
            print(f"[⚠️] Skipping {event_name} because metadata.txt is missing")
            continue

        metadata = read_metadata_txt(metadata_path)
        venue = metadata.get("venue", "")
        raw_date = metadata.get("Event Date", "").strip()
        date = raw_date if raw_date else None
        metadata_json = json.dumps(metadata)

        # 🔁 Delete event if already exists
        cursor.execute("SELECT id FROM events WHERE event_name = %s", (event_name,))
        existing = cursor.fetchone()
        if existing:
            existing_id = existing[0]
            print(f"[♻️] Event '{event_name}' exists. Removing old records (ID: {existing_id})...")
            cursor.execute("DELETE FROM matched_photos WHERE event_id = %s", (existing_id,))
            cursor.execute("DELETE FROM events WHERE id = %s", (existing_id,))
            conn.commit()

        # Insert event
        try:
            cursor.execute("""
                INSERT INTO events (event_name, venue, date, metadata)
                VALUES (%s, %s, %s, %s)
            """, (event_name, venue, date, metadata_json))
            conn.commit()
            event_id = cursor.lastrowid
            event_count += 1
            print(f"[📁] Inserted event: {event_name} (ID: {event_id}) ✅")
        except Exception as e:
            print(f"[❌] Failed to insert event {event_name}: {e}")
            continue

        image_files = [
            os.path.join(event_path, f)
            for f in os.listdir(event_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not image_files:
            print(f"[⚠️] No images found in {event_name}")
            continue

        print(f"[🚀] Encoding {len(image_files)} photos using multiprocessing (2 workers)...")
        with Pool(processes=2) as pool:
            results = list(tqdm(pool.imap_unordered(
                process_image, [(img, event_id) for img in image_files]),
                total=len(image_files),
                desc=f"Encoding '{event_name}'", unit="image"
            ))

        encoded_count = sum(results)
        total_faces += encoded_count
        print(f"[✅] Finished event: {event_name} — Encoded {encoded_count}/{len(image_files)}\n")

    conn.close()
    print(f"\n[🏁] All done. Total events: {event_count}, total faces encoded: {total_faces}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
