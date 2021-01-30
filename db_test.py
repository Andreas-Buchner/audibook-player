import sqlite3

db = sqlite3.connect("FilesDB.db")
books = db.execute("SELECT * FROM books ORDER BY name").fetchall()
for b in books:
    print(b)
