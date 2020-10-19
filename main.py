import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # surpresses the unnecessary output of pygame version at import.
import sqlite3
import time
from pygame import mixer


def initialize():
    connection = sqlite3.connect("FilesDB.db")
    connection.row_factory = lambda cursor, row: row[0]  # changes the weird output format to normal one
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Books ('
              'name TEXT PRIMARY KEY,'
              'heard INTEGER'
              ')')
    books = os.listdir("../Audiobooks")  # hardcoded to be path to USB Stick
    stored = cursor.execute('SELECT name FROM Books').fetchall()
    print(stored)
    for book in stored:
        print(book)
        if book not in books:
            cursor.execute('DELETE FROM Books WHERE name = ?', book)
            cursor.execute('DROP TABLE IF EXISTS ?', book)

    for book in books:
        if book not in stored:
            cursor.execute("""
                      INSERT INTO Books (name, heard)
                      VALUES (?,?) 
                      """, (book, 0))
            cursor.execute("""CREATE TABLE IF NOT EXISTS ? (
                           path TEXT PRIMARY KEY,
                           heard INTEGER,
                           )""", book)

    # database, delete all entries that are not in the current book list -> have already been heard
    # add all new books to list
    for book in books:
        # drop all tables of read books here

        titles = os.listdir("../Audiobooks/{}".format(book))
        print(len(titles))

    cursor.close()
    connection.commit()
    connection.close()


def main():
    initialize()
    #t = initialize()
    #test = t[1]
    #print(test)

    #mixer.init()
    #mixer.music.load("../Audiobooks/SeaulenDerErde/{}".format(test))
    #mixer.music.play()
    #while mixer.music.get_busy():
    #    time.sleep(1)
    #    print("sleeping")
    #print("finished")


if __name__ == '__main__':
    main()
