from pygame import mixer
import os
import time


def initialize():
    books = os.listdir("../Audiobooks")  # hardcoded to be path to USB Stick
    # database, delete all entries that are not in the current book list -> have already been heard
    # add all new books to list
    for book in books:
        # drop all tables of read books
        titles = os.listdir("../Audiobooks/{}".format(book))
        print(len(titles))
        return titles  # delete this, just for testin


def main():
    t = initialize()
    test = t[1]
    print(test)

    mixer.init()
    mixer.music.load("../Audiobooks/SeaulenDerErde/{}".format(test))
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(1)
        print("sleeping")
    print("finished")


if __name__ == '__main__':
    main()
