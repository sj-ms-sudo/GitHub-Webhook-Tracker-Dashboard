import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('auth.db')
c = conn.cursor()
c.execute("""
          CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
          password  TEXT NOT NULL)""")
pw_hash = generate_password_hash("admin123")
c.execute("INSERT INTO users (username,password) VALUES (?,?)",("Admin",pw_hash))
conn.commit()
conn.close()
