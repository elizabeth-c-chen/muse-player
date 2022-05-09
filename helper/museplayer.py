# Imports
import time
import threading
import ffpyplayer.tools
from ffpyplayer.player import MediaPlayer
from datetime import datetime
from pytz import timezone
from .DataStructures import SongQueue, SongItem
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
    minutes = int(num_seconds//60)
    seconds = int((num_seconds/60 - minutes)*60)
    if seconds < 10:
        seconds = str(0) + str(seconds)
    return f"{minutes}:{seconds}"
    
def update_num_plays(db_songs_collection, song_to_update: SongItem):
    db_songs_collection.update_one({'_id': song_to_update.song_id}, {'$inc': {'numPlays': 1}})
    return True


class MusePlayer:
    def __init__(self, repeat_type=1):
        # Initialize with a random song!
        rand_song = songs.aggregate([{"$sample": {"size": 1}}]).next()
        self.now_playing = SongItem(rand_song)
        # ff_opts 
        options = {
            'paused': True,  # always initialize upon launch with a paused player
            'loop': repeat_type,
            'vn': True,
            'sn': True,
            'acodec': self.now_playing.codec
        }
        # Initialize with an empty queue that can hold future songs
        self.queue = SongQueue()
        # The media player object
        self.player = MediaPlayer(
            filename=self.now_playing.file_path,
            ff_opts=options
        )
        # Thread 
        self.wait_play = threading.Thread(target=self.sleeper_function, args=())
        # If repeat mode is changed during playback, this will update and inform the next player
        self.next_repeat_type = repeat_type
        self.next_player = None
        self.next_song = None
        self.song_has_changed = 0
        self.set_next_song()
        
    def get_player(self):
        return self.player
    
    def get_queue(self):
        return self.queue
    
    def get_now_playing(self):
        return self.now_playing

    def get_song_has_changed(self):
        return self.song_has_changed
    
    def get_elapsed_and_remaining_time(self):
        elapsed = self.get_player().get_pts()
        duration = self.get_player().get_metadata()['duration']
        remaining = duration - elapsed
        return {
            'songHasChanged': self.get_song_has_changed(),
            'elapsedTime': format_seconds(elapsed),
            'remainingTime': format_seconds(remaining),
            'elapsedSeconds': elapsed, 
            'remainingSeconds': remaining, 
            'durationSeconds': duration
        }

    def sleeper_function(self):
        play_counted = False
        while self.get_player().get_metadata()['duration'] - self.get_player().get_pts() > 3:
            if play_counted is False and self.get_player().get_pts() / self.get_player().get_metadata()['duration'] > 0.65:
                play_counted = update_num_plays(songs, self.get_now_playing())
            time.sleep(2)
        #self.autoplay_next()
       # if self.get_player().get_metadata()['duration'] - self.get_player().get_pts() < 0.5:
       #     return
        
    def seek_forward(self):
        if self.player.get_pause() is False:
            self.player.seek(pts=10, relative=True)

    def seek_backward(self):
        if self.player.get_pause() is False:
            self.player.seek(pts=-10, relative=True)
    
    def set_next_repeat_type(self, new_repeat_type):
        self.next_repeat_type = new_repeat_type
    

    # Create player for a given song (used only after initialization)
    def make_new_player(self, song: SongItem):
        options = {
            'paused': True, 
            'loop': self.next_repeat_type,
            'vn': True,
            'sn': True, 
            'acodec': song.codec
        }
        new_player = MediaPlayer(
            filename=song.file_path,
            ff_opts=options
        )
        return new_player
    
    def play_or_pause(self):
        """Function triggered by the play/pause media control button"""
        if self.player.get_pause() is True and self.player.get_pts() < 1:
            self.wait_play.start()
            self.player.set_pause(False)
        elif self.player.get_pause() is True and self.player.get_pts() > 0.0:
            self.player.set_pause(False)
        elif self.player.get_pause() is False:
            self.player.set_pause(True)

    def set_next_song(self):
        if self.next_repeat_type == 0: # repeat same song infinitely
            next_song = self.now_playing
        elif self.next_repeat_type == 1: # play current song just once
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
        
    def autoplay_next(self):
        """
        ATTENTION @me 
        autoplay function is broken
        wait_play issue
        problem w/ threading/sleeper function 
        creating next_player
        #TODO go here first
        """
        self.song_has_changed = 1 # will trigger page reload via javascript
        self.player = self.next_player
        self.now_playing = self.next_song
        self.wait_play = threading.Thread(target=self.sleeper_function, args=())
        self.wait_play.start()
        self.player.set_pause(False)
        self.set_next_song()

    # def switch_song(self, new_song: SongItem):
    #     new_player, options = self.make_new_player(new_song)
    #     self.player.close_player()
    #     self.player = new_player
    #     self.wait_play = threading.Thread(target=self.sleeper_function, args=())
    #     self.wait_play.start()
    #     self.now_playing = new_song
