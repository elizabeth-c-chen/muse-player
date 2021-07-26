from datetime import date


class Playlist:
    def __init__(self, title=f"New Playlist {date.today()}"):
       self.songs_list = []
       self.songs_list = DoublyLinkedList()