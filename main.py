import os
import sqlite3

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # surpresses the unnecessary output of pygame version at import.
import time
from pygame import mixer
from gpiozero import Button

# Start the script with a paused input so if there would be a power loss the audiobooks won't start playing alone
PLAYING_PAUSED = True


def initialize(connection, cursor):
    """

    :param connection: connection to Database (Connection)
    :param cursor: cursor pointing to Database (Cursor)
    :return: None

    This Function reads out all the folders stored on the USB Stick and assumes they are containing full Audiobooks
    It creates a Database with a main Table called books and another table for each book, that table has the name of the
    book
    In the books table the name and whether the book has been heard as its whole is stored
    In the other table of each book the path of each file (e.g. book/chapter1.mp3) is stored and whether the file has been
    heard
    """

    cursor.execute('CREATE TABLE IF NOT EXISTS Books ('
              'name TEXT PRIMARY KEY,'
              'heard INTEGER'
              ')')
    connection.commit()

    onUSB = os.listdir("../../../media/pi/STICK/Audiobooks")  # hardcoded to be path to USB Stick
    print("----------------INIT----------------")
    print("Found on USB:")
    print(onUSB)
    stored = cursor.execute('SELECT name FROM Books').fetchall()
    print("\nAlready stored in DB:")
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

        titles = os.listdir("../../../media/pi/STICK/Audiobooks/{}".format(book))
        for title in titles:
	    print("{}/{}".format(book, title))
            cursor.execute("""
                      INSERT OR IGNORE INTO {} (path, heard)
                      VALUES (?,?)
                      """.format(book), (book + "/" + title, 0))
            connection.commit()


def update_book_heard(connection, cursor, book):
    """

    :param connection: connection to Database (Connection)
    :param cursor: cursor pointing to Database (Cursor)
    :param book: book that should be checked if it is heard (String)
    :return: None

    This updates the read column for a specific book in the books table
    It checks whether all the titles of the book have been heard or if there even are any titles
    """
    books = cursor.execute("SELECT * FROM {}".format(book)).fetchall()
    if len(books) == 0:  # no audio files available for book
        cursor.execute("UPDATE books SET heard = 1 WHERE name = '{}'".format(book))
        connection.commit()
    else:
        count = cursor.execute("SELECT * FROM {} WHERE heard = 0".format(book))
        if count == 0:
            cursor.execute("UPDATE books SET heard = 1 WHERE name = '{}'".format(book))
            connection.commit()


def set_title_heard(connection, cursor, path):
    """
    :param connection: connection to Database (Connection)
    :param cursor: cursor pointing to Database (Cursor)
    :param path: containing book and title that should be marked as read
    :return: None

    This function simply marks a specific title of a book as heard
    """
    path = path.split("/")
    book = path[0]
    title = path[1]
    cursor.execute("UPDATE {} SET heard = 1 WHERE path = '{}'".format(book, book + "/" + title))
    connection.commit()


def toggle_pause():
    global PLAYING_PAUSED
    PLAYING_PAUSED = not PLAYING_PAUSED


def main():
    connection = sqlite3.connect("FilesDB.db")

    global PLAYING_PAUSED

    button = Button(18)
    button.when_pressed = toggle_pause

    # Changes the output format so we are only getting first column though which is perfectly fine in our case
    connection.row_factory = lambda cursor, row: row[0]
    cursor = connection.cursor()

    initialize(connection, cursor)  # builds and/or updates database

    books = cursor.execute("SELECT * FROM books").fetchall()
    print("\n ----------------MAIN----------------")

    for book in books:
        update_book_heard(connection, cursor, book)

    current_book = cursor.execute("SELECT * FROM books WHERE heard = 0").fetchone()
    # MAIN LOOP THAT PLAYS THE TITLE
    while current_book is not None:  # no unheard books left
        print("\nCurrent Book is:")
        print(current_book)

        current_title = cursor.execute("SELECT * FROM {} WHERE heard = 0".format(current_book)).fetchone()
        print("\nCurrent Title is:")
        print(current_title)

        mixer.init()
        mixer.music.load("../../../media/pi/STICK/Audiobooks/" + current_title)  # again hardcode this to go to USB Stick
        mixer.music.play()  # starts the audio, don't worry it will get stopped at the beginning because
        while True:
            if PLAYING_PAUSED:
		print("Paused")
		mixer.music.pause()
                time.sleep(0.5)
            else:
                print("Playing {}".format(current_title))
                mixer.music.unpause()
                time.sleep(0.2)  # maybe we throw this away, just some extra time to toggle busy
                if not mixer.music.get_busy():  # we tried to unpause but it is still not busy --> finished
                    break
                time.sleep(0.5)

        set_title_heard(connection, cursor, current_title)
        update_book_heard(connection, cursor, current_book)
        current_book = cursor.execute("SELECT * FROM books WHERE heard = 0").fetchone()

    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
