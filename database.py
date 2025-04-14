# database.py
import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def init_db():
    """
    Initializes the SQLite database by creating the attendance table if it doesn't exist.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def mark_attendance(name):
    """
    Inserts an attendance record with the current timestamp for a recognized person.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO attendance (name, timestamp) VALUES (?, ?)", (name, timestamp))
    conn.commit()
    conn.close()
