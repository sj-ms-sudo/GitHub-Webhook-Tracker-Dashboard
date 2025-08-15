import sqlite3
def init_db():
    conn = sqlite3.connect('hook.db')
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS commits(
                   id TEXT PRIMARY KEY,
                   repo_name TEXT,
                   Committer TEXT,
                   Added TEXT,
                   Removed TEXT,
                   Modified TEXT,
                   timestamp TEXT)
                   """)
    conn.commit()
    conn.close()
if __name__ == "__main__":
    init_db()