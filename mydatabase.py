import sqlite3

con = sqlite3.connect('mashedpotatoes.db')

cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS myusertable (
  username TEXT PRIMARY KEY, 
  hash text NOT NULL
)
''')