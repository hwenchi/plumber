import subprocess
import sys

import psutil


class Actuator:
    def __init__(self, flow, data_dir):
        self.flow = flow
        self.data_dir = data_dir
        self.process = None

    def start(self):
        fn = self.flow.fn
        self.process = subprocess.Popen(
            [sys.executable, "-m", "plumber.run", fn.__module__, fn.__name__, str(self.data_dir)]
        )

    def detach(self):
        psutil.Process(self.process.pid).suspend()

    def attach(self):
        psutil.Process(self.process.pid).resume()

    def restart(self):
        self.stop()
        self.start()

    def stop(self, timeout=5):
        self.process.kill()
        self.process.wait(timeout=timeout)

    def is_running(self) -> bool:
        return self.process.poll() is None

    @property
    def pid(self):
        return self.process.pid

    @property
    def returncode(self):
        return self.process.returncode
