import threading
import queue
from fs.tempfs import TempFS

class TempFSFactory(threading.Thread):
    def __init__(self):
        super().__init__()

        self.fs_queue = queue.Queue()
        self.min_queue_size = 5

        #self.queue_locked = threading.Condition()

        self.replenish_event = threading.Event()
        self.stop_event = threading.Event()
        self._generator()

    def _generator(self):
        while self.fs_queue.qsize() < self.min_queue_size:
            temp_fs = TempFS()
            self.fs_queue.put(temp_fs)

    def run(self):
        while not self.stop_event.is_set():
            self.replenish_event.wait()
            if self.stop_event.is_set():
                return
            self.replenish_event.clear()
            print("Generating new TempFS...")
            self._generator()
        return
    
    def stop(self):
        print('Stopping TempFSFactory.')
        self.stop_event.set()
        self.replenish_event.set()

    def get_temp_fs(self):
        temp_fs = self.fs_queue.get()
        self.replenish_event.set()
        return temp_fs
    
    def get_queue_length(self):
        return self.fs_queue.qsize()