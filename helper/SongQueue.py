from queue import Queue

class SongQueue:
    def __init__(self):
        self.capacity = 100
        self.queue = Queue(maxsize=self.capacity)

    def __len__(self):
        return self.queue.qsize()

    def get_queue(self):
        return self.queue

    def add_song(self, song):
        self.queue.put(song)

    def get_song(self):
        return self.queue.get()

    def clear_queue(self):
        self.queue = Queue(max_size=self.capacity)

