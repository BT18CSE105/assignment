import sqlite3
import os
p = 'trade_data.db'
print('DB exists:', os.path.exists(p))
if os.path.exists(p):
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print('tables:', cur.fetchall())
    conn.close()
else:
    print('No DB file found')
