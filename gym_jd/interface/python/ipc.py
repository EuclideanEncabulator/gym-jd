from multiprocessing import shared_memory
import numpy as np
import subprocess

message_game = [
    ("direction", 4, 3),
    ("position", 4, 3),
    ("cur_node", 4, 3),
    ("next_node", 4, 3),
    ("wheel_direction", 4, 3),
    ("velocity", 4, 1),
]

class Process:
    def __init__(self, path):
        self.process = subprocess.Popen([path])#, "-batchmode", "-nographics"])
        self.pid = self.process.pid
        self.python_mem = shared_memory.SharedMemory(name=f"Local\\jd_python_{self.pid}", size=5, create=True)
        self.game_mem = shared_memory.SharedMemory(name=f"Local\\jd_game_{self.pid}", size=100, create=True)

    def read(self):
        offset = 0
        message = {}
        dt = np.dtype(np.float32)

        for name, size, count in message_game:
            message[name] = np.frombuffer(self.game_mem.buf, offset=offset, count=count, dtype=dt)
            offset += size * count

        return message

    def write(self, message):
        pass

    def destroy(self):
        self.python_mem.close()
        self.game_mem.close()

        self.python_mem.unlink()
        self.game_mem.unlink()
            