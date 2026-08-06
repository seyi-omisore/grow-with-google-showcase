import sqlite3

conn = sqlite3.connect('energy_optimizer.db')
conn.executescript(open('schema.sql').read())
conn.commit()

cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in cur.fetchall()])
