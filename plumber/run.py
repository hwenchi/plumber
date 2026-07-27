import importlib
import sys

from plumber.gauge import Gauge
from plumber.loop import run_forever
from plumber.pipe import NullPipe, Pipe
from plumber.valve import Valve


def main():
    module_name, flow_name, data_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    module = importlib.import_module(module_name)

    try:
        flow = getattr(module, flow_name)
    except AttributeError:
        raise ValueError(f"no valve named '{flow_name}' found in module '{module_name}'")

    inlet = Pipe(data_dir, flow.inlet) if flow.inlet is not None else NullPipe()
    outlet = Pipe(data_dir, flow.outlet) if flow.outlet is not None else NullPipe()
    gauge = Gauge(data_dir, flow.id)
    valve = Valve(flow, inlet, outlet, gauge)

    run_forever(valve)


if __name__ == "__main__":
    main()
