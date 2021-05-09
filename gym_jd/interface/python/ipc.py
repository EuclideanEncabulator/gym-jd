import json
import subprocess
from ctypes import windll
from ctypes import wintypes as win
from multiprocessing import shared_memory
from struct import calcsize, pack, unpack

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

with open(pkg_resources.resource_filename("extra", "message_sizes.json")) as file:
    message_types = json.load(file)
    message_game = message_types[0].items()
    message_python = message_types[1].items()

class Process:
    def __init__(self, path, graphs):
        arguments = [path, "-batchmode", "-nographics"] if graphs == True else [path]

        self.process = subprocess.Popen(arguments)
        self.pid = self.process.pid
        self.python_mem = shared_memory.SharedMemory(name=f"Local\\jd_python_{self.pid}", size=10, create=True)
        self.game_mem = shared_memory.SharedMemory(name=f"Local\\jd_game_{self.pid}", size=53, create=True)
        self.python_mutex = create_mutex(None, True, f"Local\\jd_python_mutex_{self.pid}")
        self.game_mutex = create_mutex(None, True, f"Local\\jd_game_mutex_{self.pid}")

    def read(self, wait=True):
        if wait:
            release_mutex(self.game_mutex)
            wait_for_single_object(self.game_mutex, 0xFFFFFFFF, False)

        offset = 0
        message = {}

        for name, (fmt, count) in message_game:
            dt = np.dtype(fmt)
            message[name] = np.frombuffer(self.game_mem.buf, offset=offset, count=count, dtype=dt)
            offset += dt.itemsize * count
        return message

    def write(self, message, wait=True):
        to_write = b""
        for name, (fmt) in message_python:
            to_write += pack(fmt, message[name])
        self.python_mem.buf[:] = to_write

        if wait:
            release_mutex(self.python_mutex)
            wait_for_single_object(self.python_mutex, 0xFFFFFFFF, False)

    def destroy(self):
        self.python_mem.close()
        self.game_mem.close()

        self.python_mem.unlink()
        self.game_mem.unlink()
