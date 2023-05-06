import threading
import queue
import shutil
from pathlib import Path
import fs
from fs.tempfs import TempFS
from fs.copy import copy_fs
import time

class TempFSFactory(threading.Thread):
    def __init__(self, root_folder, queue_size = 5):
        super().__init__()
        self.sourceFS = root_folder

        self.queues = {} # Dictionary of queues
        self.min_queue_size = queue_size

        cwd = Path.cwd()
        self.tempFS_dir = cwd / 'temp'
        Path(self.tempFS_dir).mkdir(parents=True, exist_ok=True)

        self.replenish_event = threading.Event()
        self.stop_event = threading.Event()

        # Create a set of TempFS for each user folder in sourceFS
        self._startup()

    def _startup(self):
        '''Given a source directory, create a list of TempFolder queues for each subfolder.'''
        root_path = str(self.sourceFS)
        with fs.open_fs(root_path) as root:
            for dir_name in root.walk.dirs():
                dir_path = fs.path.combine(root_path, dir_name)
                queue_name = str(dir_name)[1:]
                self.queues[queue_name] = queue.Queue()
                self._generator(dir_path, self.queues[queue_name])
            print(self.queues)
            return

    def _generator(self, raw_folder, TempFolder_queue):
        '''Given a source directory, create a queue of temporary filesystems for that directory.'''
        while TempFolder_queue.qsize() < self.min_queue_size:
            timestamp = str(int(time.time()))
            folder_path = Path(raw_folder)
            folder_name = folder_path.name
            tempFS_name = timestamp+folder_name
            # Need to rewrite FTP protocol to not close the FS on every action
            tempFS = TempFS(tempFS_name, temp_dir=self.tempFS_dir, auto_clean=False)
            copy_fs(raw_folder, tempFS)
            TempFolder_queue.put(tempFS)
        return

    def run(self):
        while not self.stop_event.is_set():
            self.replenish_event.wait()
            if self.stop_event.is_set():
                return
            self.replenish_event.clear()
            #print("Generating new TempFS...")
            # Should implement a way to signal which UserFolder to Generate!
            root_path = str(self.sourceFS)
            with fs.open_fs(root_path) as root:
                for dir_name in root.walk.dirs():
                    dir_path = fs.path.combine(root_path, dir_name)
                    queue_name = str(dir_name)[1:]
                    self._generator(dir_path, self.queues[queue_name])
        return
    
    def stop(self):
        print('Stopping TempFSFactory.')
        self.stop_event.set()
        self.replenish_event.set()
        # Cleanup here?
        shutil.rmtree(self.tempFS_dir)

    def get_temp_fs(self, userHome):
        # Grab a TempFS from the correct user queue
        temp_fs = self.queues[userHome].get()
        tempFS_path = temp_fs.getsyspath('/')
        print(tempFS_path)
        self.replenish_event.set()
        return tempFS_path
    
    def get_queue_length(self):
        return self.fs_queue.qsize()
