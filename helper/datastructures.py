from datetime import datetime
from queue import Queue

def format_seconds(num_seconds):
    minutes = int(num_seconds//60)
    seconds = int((num_seconds/60 - minutes)*60)
    if seconds < 10:
        seconds = str(0) + str(seconds)
    return f"{minutes}:{seconds}"
    

# SongItem class
class SongItem:
    def __init__(self, song_entry):
        self.song_id = song_entry["_id"]
        self.file_path = song_entry["songFileLoc"]
        self.artwork_path = song_entry["albumArtworkLoc"]
        self.title = song_entry["title"]
        self.artist = song_entry["artistName"]
        self.album = song_entry["albumName"]
        self.album_artist = song_entry["albumArtist"]
        self.track_number = song_entry["trackNumber"]
        self.duration = format_seconds(song_entry["duration"])
        self.num_plays = song_entry["numPlays"]
        self.last_played = song_entry["lastPlayed"]
        self.bitrate = song_entry["bitrate"]
        self.codec = song_entry["codec"]
        self.is_favorited = song_entry["isFavorited"]

def create_album_songs_list(result_songs_list: list):
    songs_list = []
    for song_result in result_songs_list:
        songs_list.append(SongItem(song_result))
    return songs_list

class AlbumItem:
    def __init__(self, title, artist, album_cover_art, album_songs):
        self.title = title
        self.artist = artist
        self.cover_art = album_cover_art
        self.songs = album_songs #create_album_songs_list(album_songs)


class PlaylistItem:  # akin to listnode
    def __init__(self, song_item: SongItem):
        self.prev = None
        self.next = None
        self.content = song_item


class DoublyLinkedSongList:
    def __init__(self):
        self.prev_song = PlaylistItem(None)  # pseudo-node
        self.next_song = PlaylistItem(None)  # pseudo-node
        self.prev_song.next = self.next_song
        self.next_song.prev = self.prev_song
        self._length = 0

    def __len__(self):
        return self._length

    def get_last(self):
        """ Returns the last item (psedu-node is skipped).
        Raises IndexError when no item exists. """
        if self._length == 0:
            raise IndexError("Try to get item from an empty playlist")
        return self.next_song.prev

    def insert_first(self, item):
        item.prev = self.prev_song
        item.next = self.prev_song.next
        self.prev_song.next = item
        self.prev_song.next.next.prev = item
        self._length += 1

    def insert_middle(self, item):
        self._length += 1
        pass

    def insert_last(self, item):
        prev_item = self.next_song.prev
        item.next = prev_item.next
        self.next_song.prev.next = item
        item.prev = self.next_song.prev
        self._length += 1

    def remove(self, item):
        item.prev.next = item.prev.next.next
        item.next.prev = item.prev
        self._length -= 1

    def __str__(self):
        return str(self.prev_song)


class Playlist:
    def __init__(self, title=f"New Playlist {datetime.now()}"):
        self.title = title
        self.map = {}
        self.songs_list = DoublyLinkedSongList()
        self.final_index = 0

    def __len__(self):
        return len(self.songs_list)

    def __contains__(self, key):
        return key in self.map

    def rename_playlist(self, new_name):
        self.title = new_name

    # Add to bottom of playlist
    def append_song(self, song_item: SongItem):
        item_to_add = PlaylistItem(self.final_index, song_item)
        if song_item.song_id not in self.map:
            self.map[song_item.song_id] = [item_to_add]
            self.songs_list.insert_last(item_to_add)
            self.songs_list.insert_last(item_to_add)
            self.final_index += 1
            return 0  # Success code
        else:
            return 999  # Error code 999 = duplicate song being added

    def remove_song(self, song_id):
        if song_id in self.map:
            item_to_remove = self.map[song_id]
            self.songs_list.remove(item_to_remove)
            self.map.pop(song_id)
            return 0  # Success code
        else:
            return 404  # Error code 404 = song not found

    def reorder(self, selected_song):
        pass

    def items(self):
        """
        Return all song_id, song_item pairs in order
        """
        kv_pairs = []
        curr_song = self.songs_list.prev_song
        while curr_song.content is not None:
            kv_pairs.append(curr_song.content)
            curr_song = curr_song.next
        return kv_pairs


class SongQueue:
    def __init__(self):
        self.capacity = 100
        self.queue = Queue(maxsize=self.capacity)

    def __len__(self):
        return self.queue.qsize()

    def get_queue(self):
        return self.queue

    def add_song(self, song: SongItem):
        self.queue.put(song)

    def get_song(self):
        return self.queue.get()

    def clear_queue(self):
        self.queue = Queue(max_size=self.capacity)