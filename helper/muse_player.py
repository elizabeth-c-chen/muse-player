from ffpyplayer.player import MediaPlayer
import time
from SongQueue import SongQueue
import os
MUSIC_DIR = os.environ.get("MUSIC_DIR")


class MusePlayer:

    def __init__(self, filepath, repeat_type=-1):
        self.curr_file = filepath
        self.repeat_type = repeat_type
        self.opts = {'paused': True, 'loop': self.repeat_type}
        self.crossfade = 5
        self.player = MediaPlayer(
            self.curr_file,
            ff_opts=self.opts
        )
        self.queue = SongQueue()
        file = MUSIC_DIR + "/P!nk/The Truth About Love/04 Just Give Me A Reason (feat. Nate Ruess).m4a"
        # self.next_file
        self.queue.add_song(file)
        self.next_repeat_type = self.repeat_type

    # Set / Get methods
    def get_player(self):
        return self.player

    def set_opts(self, opts):
        self.opts = opts

    def set_next_repeat_type(self, repeat_type):
        self.next_repeat_type = repeat_type
    
    # Functions for controlling audio player
    def play(self):
        self.player.set_pause(False)
        while self.player.get_metadata()['duration'] - self.player.get_pts() > self.crossfade:
            time.sleep(1)
            print(self.player.get_metadata()['duration'] - self.player.get_pts())
        self.prep_play_next()
        self.play()

    def pause(self):
        self.player.set_pause(True)

    def seek_forward(self, n_clicks):
        for i in range(n_clicks):
            self.player.seek(pts=10, relative=True)

    def seek_backward(self, n_clicks):
        for i in range(n_clicks):
            self.player.seek(pts=-10, relative=True)

    # Create of new player for a new song
    def make_next_player(self):
        if self.repeat_type != self.next_repeat_type:
            opts = {'paused': True, 'loop': self.next_repeat_type}
        else:
            opts = self.opts
        if self.next_repeat_type == 1:  # repeat one
            next_file = self.curr_file
        else:
            if len(self.queue) > 0:
                next_file = self.queue.get_song()
            else:
                next_file = MUSIC_DIR + "/Users/elizabethchen/Desktop/music/Maroon 5/Overexposed (Deluxe Version)/02 Payphone (feat. Wiz Khalifa).m4a"
        next_player = MediaPlayer(
            next_file,
            ff_opts=opts
        )
        return opts, next_file, next_player

    def prep_play_next(self):
        if len(self.queue) > 0:
            opts, next_file, next_player = self.make_next_player()
        self.player.close_player()
        self.curr_file = next_file
        self.repeat_type = self.next_repeat_type
        self.opts = opts
        self.player = next_player
        self.next_repeat_type = self.repeat_type
