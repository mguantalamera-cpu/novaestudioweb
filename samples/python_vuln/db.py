import sqlite3


def run_query(user):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = '" + user + "'")
    return cursor.fetchall()
