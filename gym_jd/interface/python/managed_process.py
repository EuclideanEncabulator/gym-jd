import pkg_resources

from gym_jd.interface.python.ipc import Process
from gym_jd.interface.python.injector import inject
from time import sleep

class ManagedProcess(Process):
    def __init__(self, path, graphics=True, resolution=1080):
        self.path, self.graphics, self.resolution = path, graphics, resolution

        self.start()

    def start(self):
        super().__init__(self.path, self.graphics, self.resolution)
        sleep(10) # TODO: Move to c++, we can tell when unity has loaded

        dll_path = pkg_resources.resource_filename("extra", "jelly_drift_interface.dll")
        inject(self.pid, dll_path.encode("ascii"))
        sleep(0.1)

    def safety_restart(self):
        if self.process.poll() is not None:
            print("Process Crashed, Restarting...")
            
            self.destroy()
            self.start()

    def read(self, wait):
        self.safety_restart()
        return super().read(wait=wait)

    def write(self, message, wait):
        self.safety_restart()
        return super().write(message, wait=wait)
