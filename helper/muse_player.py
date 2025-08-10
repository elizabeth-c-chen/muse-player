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
        # The media player object
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

        # If repeat mode is changed during playback, this will update and inform the next player
        self.next_repeat_mode = repeat_mode
        self.next_player = None
        self.next_song = None
        self.song_has_changed = 0
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

    def get_song_has_changed(self):
        return self.song_has_changed
    
    def get_elapsed_and_remaining_time(self):
        meta = self.get_player().get_metadata()
        duration = meta.get('duration') if meta else None
        if duration is None:
            # Metadata not ready yet, return defaults or zeros
            return {
                'songHasChanged': self.get_song_has_changed(),
                'elapsedTime': "0:00",
                'remainingTime': "0:00",
                'elapsedSeconds': 0,
                'remainingSeconds': 0,
                'durationSeconds': 0
            }
        
        elapsed = self.get_player().get_pts()
        remaining = duration - elapsed if elapsed is not None else duration
        
        return {
            'songHasChanged': self.get_song_has_changed(),
            'elapsedTime': format_seconds(elapsed) if elapsed is not None else "0:00",
            'remainingTime': format_seconds(remaining) if remaining is not None else "0:00",
            'elapsedSeconds': elapsed if elapsed is not None else 0,
            'remainingSeconds': remaining if remaining is not None else 0,
            'durationSeconds': duration
        }


    def seek_forward(self):
        if self.player.get_pause() is False:
            self.player.seek(pts=10, relative=True)

    def seek_backward(self):
        if self.player.get_pause() is False:
            self.player.seek(pts=-10, relative=True)
    
    def set_next_repeat_mode(self, new_repeat_mode):
        self.next_repeat_mode = new_repeat_mode
    
    def toggle_shuffle_mode(self):
        if self.shuffle_mode == 0: # off
            self.shuffle_mode = 1 # off to on
        elif self.shuffle_mode == 1: # on
            self.shuffle_mode = 0  # on to off
        return self.shuffle_mode
    
    def toggle_repeat_mode(self):
        if self.next_repeat_mode == 0:
            self.next_repeat_mode = 1  # 'none' → 'all'
        elif self.next_repeat_mode == 1:
            self.next_repeat_mode = 2  # 'all' → 'one'
        else:
            self.next_repeat_mode = 0  # 'one' → 'none'
        return self.next_repeat_mode  # return it so frontend can display the new state

    # Create player for a given song (used only after initialization)
    def make_new_player(self, song: SongItem):
        options = {
            'paused': True, 
            'loop': self.next_repeat_mode,
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
        if self.player.get_pause() is True: # and self.player.get_pts() == 0.25:
            self.player.set_pause(False)
        elif self.player.get_pause() is True and self.player.get_pts() > 0.0:
            self.player.set_pause(False)
        elif self.player.get_pause() is False:
            self.player.set_pause(True)

    def set_next_song(self):
        if self.next_repeat_mode == 0: # repeat same song infinitely
            next_song = self.now_playing
        elif self.next_repeat_mode == 1: # play current song just once
            if len(self.queue) > 0: # get song from queue if queue is not empty
                next_song = self.queue.get_song()
            else: # if queue is empty, play something random
                rand_song = songs.aggregate([{"$sample": {"size": 1}}]).next()
                next_song = SongItem(rand_song)
        self.next_player = self.make_new_player(next_song)
        self.next_song = next_song
        time.sleep(2)
       # print(next_song.title, next_song.artist)
        self.song_has_changed = 0
    
    def sleeper_function(self):
        play_counted = False
        while not self.stop_thread_event.is_set():
            meta = self.player.get_metadata()
            duration = meta.get('duration') if meta else None
            elapsed = self.player.get_pts() if self.player else None

            if duration is None or elapsed is None:
                # Metadata not ready yet, wait a bit and retry
                self.stop_thread_event.wait(1)
                continue

            if duration - elapsed > 3:
                if not play_counted and elapsed / duration > 0.65:
                    update_num_plays(songs, self.now_playing)
                    play_counted = True
            else:
                break

            self.stop_thread_event.wait(2)


    def stop_playback_monitor(self):
        self.stop_thread_event.set()
        if self.wait_play.is_alive():
            self.wait_play.join()

    def autoplay_next(self):
        self.song_has_changed = 1
        # Stop current monitor thread cleanly
        self.stop_playback_monitor()

        if self.player:
            self.last_song = self.now_playing
            self.player.close_player()
        
        
        self.player = self.next_player
        self.now_playing = self.next_song

        # Clear the event and restart the monitor thread
        self.stop_thread_event.clear()
        self.wait_play = threading.Thread(target=self.sleeper_function)
        self.wait_play.start()

        self.player.set_pause(False)
        self.set_next_song()


    #     def sleeper_function(self):
    #     play_counted = False
    #     while self.get_player().get_metadata()['duration'] - self.get_player().get_pts() > 3:
    #         if play_counted is False and self.get_player().get_pts() / self.get_player().get_metadata()['duration'] > 0.65:
    #             play_counted = update_num_plays(songs, self.get_now_playing())
    #         time.sleep(2)
    #     #self.autoplay_next()
    #    # if self.get_player().get_metadata()['duration'] - self.get_player().get_pts() < 0.5:
    #    #     return

    # def autoplay_next(self):
    #     """
    #     ATTENTION @me 
    #     autoplay function is broken
    #     wait_play issue
    #     problem w/ threading/sleeper function 
    #     creating next_player
    #     #TODO go here first
    #     """
    #     self.song_has_changed = 1  # will trigger page reload via javascript
        
    #     if self.player:
    #         self.last_song = self.now_playing
    #         self.player.close_player()  # close the current player to free resources
        
    #     self.player = self.next_player
    #     self.now_playing = self.next_song
        
    #     # Restart the playback monitoring thread (you'll want to fix threading, see later)
    #     self.wait_play = threading.Thread(target=self.sleeper_function)
    #     self.wait_play.start()
        
    #     self.player.set_pause(False)
    #     self.set_next_song()

    # def switch_song(self, new_song: SongItem):
    #     new_player, options = self.make_new_player(new_song)
    #     self.player.close_player()
    #     self.player = new_player
    #     self.wait_play = threading.Thread(target=self.sleeper_function, args=())
    #     self.wait_play.start()
    #     self.now_playing = new_song
