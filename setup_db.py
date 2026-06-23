import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Old database removed.")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0
)
""")

hashed_password = generate_password_hash("JuniorMember#CTF26")

cursor.execute("""
INSERT INTO users (username, password, is_admin, score)
VALUES (?, ?, 1, 0)
""", ("jmadmin", hashed_password))

conn.commit()
conn.close()

print("✅ Database setup complete! Admin user created (username: jmadmin)")