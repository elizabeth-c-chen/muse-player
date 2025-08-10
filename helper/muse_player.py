# Imports
import time
import threading
import ffpyplayer.tools
from ffpyplayer.player import MediaPlayer
from datetime import datetime
from pytz import timezone
from .data_structures import SongQueue, SongItem, format_seconds
from pymongo import MongoClient


# TODO fix autoplay_next/threading

# ffpyplayer log level
ffpyplayer.tools.set_loglevel("info") # change to error for production

# Database Setup
connection = MongoClient("mongodb://127.0.0.1:27017/museplayer")
db = connection.museplayer
albums = db.albums
artists = db.artists
songs = db.songs




def format_seconds(num_seconds):
    minutes, seconds = divmod(int(num_seconds), 60)
    return f"{minutes}:{seconds:02d}"
    
def update_num_plays(db_songs_collection, song_to_update: SongItem):
    db_songs_collection.update_one({'_id': song_to_update.song_id}, {'$inc': {'numPlays': 1}})
    return True


class MusePlayer:
    def __init__(self, repeat_mode=1, shuffle_mode=0):
        # Initialize with a random song!
        rand_song = songs.aggregate([{"$sample": {"size": 1}}]).next()
        self.now_playing = SongItem(rand_song)
        # ff_opts 
        options = {
            'paused': True,  # always initialize upon launch with a paused player
            'loop': repeat_mode,
            'vn': True,
            'sn': True,
            'acodec': self.now_playing.codec
        }
        # Initialize with an empty queue that can hold future songs
        self.queue = SongQueue()
        # Maybe want to save queue state upon quit and then restore?? 
        
        # Media player object
        self.player = MediaPlayer(
            filename=self.now_playing.file_path,
            ff_opts=options
        )
        time.sleep(0.25)  # wait for player to initialize
        self.repeat_mode = repeat_mode
        self.shuffle_mode = shuffle_mode

        # Thread 
        self.stop_thread_event = threading.Event()
        self.wait_play = threading.Thread(target=self.sleeper_function)
        self.wait_play.start()

        self.next_player = None
        self.next_song = None
        self.set_next_song()
        self.last_song = None  

    def get_player(self):
        return self.player
    
    def is_playing(self):
        return not self.player.get_pause()

    def get_queue(self):
        return self.queue
    
    def get_now_playing(self):
        return self.now_playing

    def get_repeat_mode(self):
        return self.repeat_mode
    
    def get_shuffle_mode(self):
        return self.shuffle_mode
    
    def get_player_info(self):
        meta = self.get_player().get_metadata()
        duration = meta.get('duration') if meta else None
        if duration is None:
            # Metadata not ready yet, return defaults or zeros
            return {
                'artist': self.now_playing.artist,
                'title': self.now_playing.title,    
                'artwork_path': self.now_playing.artwork_path,
                'elapsed_time': "0:00",
                'remaining_time': "0:00",
                'elapsed_seconds': 0,
                'remaining_seconds': 0,
                'duration_seconds': 0,
                'is_playing': self.is_playing(),
                'shuffle_mode': self.get_shuffle_mode(),
                'repeat_mode': self.get_repeat_mode()
            }
        
        elapsed = self.get_player().get_pts()
        remaining = duration - elapsed if elapsed is not None else duration
        
        return {
            'artist': self.now_playing.artist,
            'title': self.now_playing.title,    
            'artwork_path': self.now_playing.artwork_path,
            'elapsed_time': format_seconds(elapsed) if elapsed is not None else "0:00",
            'remaining_time': format_seconds(remaining) if remaining is not None else "0:00",
            'elapsed_seconds': elapsed if elapsed is not None else 0,
            'remaining_seconds': remaining if remaining is not None else 0,
            'duration_seconds': duration,
            'is_playing': self.is_playing(),
            'shuffle_mode': self.get_shuffle_mode(),
            'repeat_mode': self.get_repeat_mode()
        }

    def seek_forward(self):
        if self.player.get_pause() is False:
            self.player.seek(pts=10, relative=True)

    def seek_backward(self):
        if self.player.get_pause() is False:
            self.player.seek(pts=-10, relative=True)
    
    def toggle_shuffle_mode(self):
        if self.shuffle_mode == 0: # off
            self.shuffle_mode = 1 # off to on
        elif self.shuffle_mode == 1: # on
            self.shuffle_mode = 0  # on to off
        return self.get_shuffle_mode()  # return so frontend can display the new state
    
    def toggle_repeat_mode(self):
        if self.repeat_mode == 0: # no repeat / same as repeat all for now
            self.repeat_mode = 1 # 'none' → 'all'
        elif self.repeat_mode == 1: # repeat all 
            self.repeat_mode = 2  # 'all' → 'one'
        elif self.repeat_mode == 2: # repeat one 
            self.repeat_mode = 0  # 'one' → 'none'
        return self.get_repeat_mode()  # return so frontend can display the new state

    # Create player for a given song (used only after initialization)
    def make_new_player(self, song: SongItem):
        options = {
            'paused': True, 
            'loop': self.repeat_mode,
            'vn': True,
            'sn': True, 
            'acodec': song.codec
        }
        new_player = MediaPlayer(
            filename=song.file_path,
            ff_opts=options
        )
        time.sleep(0.25) # wait for player to initialize
        return new_player
    
    def play_or_pause(self):
        """Function triggered by the play/pause media control button"""
        if self.player.get_pause() is True:
            self.player.set_pause(False)
        elif self.player.get_pause() is False:
            self.player.set_pause(True)
        return self.player.get_pause()  # return the new state (True for paused, False for playing)

    def set_next_song(self):
        if self.repeat_mode == 0 or self.repeat_mode == 1: # play current song just once
            if len(self.queue) > 0: # get song from queue if queue is not empty
                next_song = self.queue.get_song()
            else: # if queue is empty, play something random
                rand_song = songs.aggregate([{"$sample": {"size": 1}}]).next()
                next_song = SongItem(rand_song)
        elif self.repeat_mode == 2: # repeat current song
            next_song = self.now_playing  # repeat the current song
        self.next_player = self.make_new_player(next_song)
        self.next_song = next_song
    
    def sleeper_function(self):
        play_counted = False
        while not self.stop_thread_event.is_set():
            meta = self.player.get_metadata()
            duration = meta.get('duration') if meta else None
            elapsed = self.player.get_pts() if self.player else None

            if duration is None or elapsed is None:
                # Metadata not ready yet, wait a bit and retry
                self.stop_thread_event.wait(0.25)
                continue

            remaining = duration - elapsed

            if remaining <= 5:  # song is almost over
                # Trigger next song autoplay
                self.stop_thread_event.wait(3)
                self.autoplay_next() # has 3 second sleep built in
                break  # exit this thread, new thread will start with next song

            # If at least 2/3 of the song has been played, increment play count
            if not play_counted and elapsed / duration >= 0.667:
                update_num_plays(songs, self.now_playing)
                play_counted = True
        
            self.stop_thread_event.wait(0.5)


    def stop_playback_monitor(self):
        self.stop_thread_event.set()
        if self.wait_play.is_alive() and threading.current_thread() != self.wait_play:
            self.wait_play.join()

    def autoplay_next(self):
        self.stop_playback_monitor()  # Stop current monitor thread cleanly

        if self.player:
            self.last_song = self.now_playing
            self.player.close_player()

        self.now_playing = self.next_song
        self.player = self.next_player
        time.sleep(0.5) 
        self.player.set_pause(False) # start the new player
    
        # Clear the event and restart the monitor thread
        self.stop_thread_event.clear()
        self.wait_play = threading.Thread(target=self.sleeper_function)
        self.wait_play.start()
        
        # Setup next song for autoplay
        self.set_next_song()
        

    # def switch_song(self, new_song: SongItem):
    #     new_player, options = self.make_new_player(new_song)
    #     self.player.close_player()
    #     self.player = new_player
    #     self.wait_play = threading.Thread(target=self.sleeper_function, args=())
    #     self.wait_play.start()
    #     self.now_playing = new_song
