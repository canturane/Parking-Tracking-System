import os
import cv2
import easyocr
from datetime import datetime
import sqlite3

# EasyOCR başlat
reader = easyocr.Reader(['tr'], gpu=False)

# Veritabanı yolu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "parking.db")

class PlateDetection:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT,
                entry_time TEXT,
                exit_time TEXT,
                fee REAL
            )
        ''')
        conn.commit()
        conn.close()

    def process_frame(self, frame):
        detected_plates = self.detect_text(frame)
        return detected_plates

    def detect_text(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray)
        plates = []

        for (bbox, text, prob) in results:
            if prob > 0.3:
                text = text.upper().replace(" ", "")
                if self.is_valid_plate(text):
                    plates.append(text)
                    print(f"[✓] Plaka algılandı: {text} ({prob:.2f})")
                    # Görüntüye çizim
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    top_left = tuple(map(int, top_left))
                    bottom_right = tuple(map(int, bottom_right))
                    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                    cv2.putText(frame, text, (top_left[0], top_left[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return plates

    @staticmethod
    def is_valid_plate(plate):
        if len(plate) < 7 or len(plate) > 9:
            return False
        if plate[:2].isdigit() and plate[2:5].isalpha() and plate[5:].isdigit():
            return True
        elif plate[:2].isdigit() and plate[2:4].isalpha() and plate[4:].isdigit():
            return True
        return False

    def handle_plate(self, plate):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute("SELECT * FROM parking WHERE plate = ? AND exit_time IS NULL", (plate,))
        record = cursor.fetchone()

        if record:
            entry_time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')
            duration = (now - entry_time).total_seconds()
            if duration < 10:
                print(f"[!] {plate}: 10 saniye içinde çıkış yapılamaz.")
            else:
                fee = (duration / 60) * 10
                cursor.execute("UPDATE parking SET exit_time = ?, fee = ? WHERE id = ?",
                               (now.strftime('%Y-%m-%d %H:%M:%S'), fee, record[0]))
                print(f"[✔] Çıkış: {plate}, Ücret: {fee:.2f} TL")
        else:
            cursor.execute("SELECT * FROM parking WHERE plate = ? AND exit_time IS NOT NULL ORDER BY exit_time DESC LIMIT 1", (plate,))
            last_exit = cursor.fetchone()
            if last_exit:
                last_exit_time = datetime.strptime(last_exit[3], '%Y-%m-%d %H:%M:%S')
                if (now - last_exit_time).total_seconds() < 10:
                    print(f"[!] {plate}: 10 saniye içinde tekrar giriş yapılamaz.")
                    conn.close()
                    return

            cursor.execute("INSERT INTO parking (plate, entry_time) VALUES (?, ?)",
                           (plate, now.strftime('%Y-%m-%d %H:%M:%S')))
            print(f"[✔] Giriş: {plate}")

        conn.commit()
        conn.close()
