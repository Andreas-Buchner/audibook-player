import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # surpresses the unnecessary output of pygame version at import.
import sqlite3
import time
from pygame import mixer


def initialize():
    """
    This Method reads out all the folders stored on the USB Stick and assumes they are containing full Audiobooks
    It creates a Database with a main Table called books and another table for each book, that table has the name of the
    book
    In the books table the name and whether the book has been heard as its whole is stored
    In the other table of each book the path of each file (e.g. book/chapter1.mp3) is stored and whether the file has been
    heard
    """
    connection = sqlite3.connect("FilesDB.db")
    connection.row_factory = lambda cursor, row: row[0]  # changes the weird output format to normal one
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Books ('
              'name TEXT PRIMARY KEY,'
              'heard INTEGER'
              ')')
    connection.commit()

    onUSB = os.listdir("../Audiobooks")  # hardcoded to be path to USB Stick
    print("Found on USB:")
    print(onUSB)
    stored = cursor.execute('SELECT name FROM Books').fetchall()
    print("\n Already stored in DB:")
    print(stored)
    for book in stored:
        if book not in onUSB:
            cursor.execute('DELETE FROM Books WHERE name = ?', book)
            cursor.execute('DROP TABLE IF EXISTS ?', book)
            connection.commit()

    for book in onUSB:
        if book not in stored:
            cursor.execute("""
                      INSERT INTO Books (name, heard)
                      VALUES (?,?) 
                      """, (book, 0))
            connection.commit()
            cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
                           path TEXT PRIMARY KEY,
                           heard INTEGER
                           )""".format(book))
            connection.commit()

    # database, delete all entries that are not in the current book list -> have already been heard
    # add all new books to list
    for book in onUSB:
        # drop all tables of read books here

        titles = os.listdir("../Audiobooks/{}".format(book))
        for title in titles:
            cursor.execute("""
                      INSERT OR IGNORE INTO {} (path, heard)
                      VALUES (?,?)
                      """.format(book), (book + os.path.sep + title, 0))
            connection.commit()

    cursor.close()
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
