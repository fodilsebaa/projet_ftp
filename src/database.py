import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/analysis_history.db")

def init_db():
    print(">>> init_db called")
    """Create database and table if they don't exist"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            analysis_datetime TEXT NOT NULL,
            total_patients INTEGER,
            busiest_hour TEXT,
            busiest_day TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_analysis(file_name, total_patients, busiest_hour, busiest_day):
    """Insert a new analysis record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis (
            file_name,
            analysis_datetime,
            total_patients,
            busiest_hour,
            busiest_day
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        file_name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_patients,
        busiest_hour,
        busiest_day
    ))

    conn.commit()
    conn.close()
