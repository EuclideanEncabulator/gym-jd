import json
import subprocess
from struct import pack, unpack, calcsize
from multiprocessing import shared_memory

import numpy as np

with open("config/message_sizes.json") as file:
    message_types = json.load(file)
    message_game = message_types[0].items()
    message_python = message_types[1].items()

class Process:
    def __init__(self, path):
        self.process = subprocess.Popen([path])#, "-batchmode", "-nographics"])
        self.pid = self.process.pid
        self.python_mem = shared_memory.SharedMemory(name=f"Local\\jd_python_{self.pid}", size=11, create=True)
        self.game_mem = shared_memory.SharedMemory(name=f"Local\\jd_game_{self.pid}", size=38, create=True)
        self.changed = False;

    def read(self):
        offset = 0
        while True:
            message = {}

            for name, (fmt, count) in message_game:
                size = calcsize(fmt)
                message[name] = [unpack(fmt, self.game_mem.buf[i:i+size])[0] for i in range(offset, offset + size * count, size)]

            if message["changed"][0] == self.changed:
                continue;

            self.changed = message["changed"]

            return message

    def write(self, message):
        to_write = b""
        for name, (fmt) in message_python:
            to_write += pack(fmt, message[name])
        self.python_mem.buf[:] = to_write

    def destroy(self):
        self.python_mem.close()
        self.game_mem.close()

        self.python_mem.unlink()
        self.game_mem.unlink()
            