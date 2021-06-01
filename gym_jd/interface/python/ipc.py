import json
import subprocess
from ctypes import windll
from ctypes import wintypes as win
from multiprocessing import shared_memory

import numpy as np
import pkg_resources

create_mutex = windll.kernel32.CreateMutexW
create_mutex.argtypes = [win.LPCVOID, win.BOOL, win.LPCWSTR]
create_mutex.restype = win.HANDLE

wait_for_single_object = windll.kernel32.WaitForSingleObject
wait_for_single_object.argtypes = [win.HANDLE, win.DWORD, win.BOOL]
wait_for_single_object.restype = win.DWORD

release_mutex = windll.kernel32.ReleaseMutex
release_mutex.argtypes = [win.HANDLE]
release_mutex.restype = win.BOOL

total_size = lambda message_sizes : sum(fmt.itemsize * count for fmt, count in message_sizes.values())

with open(pkg_resources.resource_filename("extra", "message_sizes.json")) as file:
    message_types = json.load(file)

    message_python = {name: (np.dtype(fmt), count) for name, (fmt, count) in message_types[1].items()}
    message_game = {name: (np.dtype(fmt), count) for name, (fmt, count) in message_types[0].items()}

class Process:
    def __init__(self, path, graphics=True, resolution=1080):
        arguments = [path, "-batchmode", "-nographics"] if graphics == False else [
            path,
            "-screen-height", str(resolution),
            "-screen-width", str(resolution * (16 / 9))
        ]

        self.process = subprocess.Popen(arguments)
        self.pid = self.process.pid
        self.python_mem = shared_memory.SharedMemory(name=f"Local\\jd_python_{self.pid}", size=total_size(message_python), create=True)
        self.game_mem = shared_memory.SharedMemory(name=f"Local\\jd_game_{self.pid}", size=total_size(message_game), create=True)
        self.python_mutex = create_mutex(None, True, f"Local\\jd_python_mutex_{self.pid}")
        self.game_mutex = create_mutex(None, True, f"Local\\jd_game_mutex_{self.pid}")

    def read(self, wait=True):
        if wait:
            release_mutex(self.game_mutex)
            wait_for_single_object(self.game_mutex, 0xFFFFFFFF, False)

        offset = 0
        message = {}

        for name, (dt, count) in message_game.items():
            message[name] = np.frombuffer(self.game_mem.buf, offset=offset, count=count, dtype=dt)
            offset += dt.itemsize * count
        return message

    def write(self, message, wait=True):
        to_write = b""
        for name, (dt, _) in message_python.items():
            to_write += np.array(message[name], dtype=dt).tobytes()

        self.python_mem.buf[:] = to_write

        if wait:
            release_mutex(self.python_mutex)
            wait_for_single_object(self.python_mutex, 0xFFFFFFFF, False)

    def destroy(self):
        self.python_mem.close()
        self.game_mem.close()

        self.python_mem.unlink()
        self.game_mem.unlink()
