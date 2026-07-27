import signal
import time

from plumber.actuator import Actuator


def _raise_keyboard_interrupt(signum, frame):
    raise KeyboardInterrupt


class Pipeline:
    def __init__(self, flows, data_dir):
        producers = {}
        for flow in flows:
            if flow.outlet is None:
                continue
            if flow.outlet in producers:
                raise ValueError(
                    f"outlet '{flow.outlet}' has more than one producer: "
                    f"'{producers[flow.outlet]}' and '{flow!r}'"
                )
            producers[flow.outlet] = repr(flow)

        for flow in flows:
            if flow.inlet is not None and flow.inlet not in producers:
                raise ValueError(f"valve '{flow!r}' has inlet '{flow.inlet}' but no valve produces it")

        self.flows = flows
        self.data_dir = data_dir
        self.actuators = {flow.id: Actuator(flow, data_dir) for flow in flows}

    def start(self):
        for actuator in self.actuators.values():
            actuator.start()

    def stop(self):
        for actuator in self.actuators.values():
            actuator.stop()

    def run(self, check_interval=1):
        self.start()
        signal.signal(signal.SIGTERM, _raise_keyboard_interrupt)

        try:
            while True:
                time.sleep(check_interval)
                for name, actuator in self.actuators.items():
                    if not actuator.is_running():
                        print(f"{name} crashed (exit code {actuator.returncode}), restarting")
                        actuator.restart()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()