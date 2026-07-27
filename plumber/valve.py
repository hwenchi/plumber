from plumber.pipe import PipeLike


class Valve:
    def __init__(self, flow, inlet: PipeLike, outlet: PipeLike, gauge):
        self.flow = flow
        self.inlet = inlet
        self.outlet = outlet
        self.gauge = gauge

    def drip(self) -> bool:
        checkpoint = self.gauge.read()

        self.outlet.truncate(checkpoint["write_offset"])

        tapped = self.inlet.tap(checkpoint["read_offset"])
        if tapped is None:
            return False
        drop_in, read_offset = tapped

        drops_out, reservoir = self.flow(drop_in, checkpoint["reservoir"])

        checkpoint["write_offset"] = self.outlet.append(drops_out)
        checkpoint["read_offset"] = read_offset
        checkpoint["reservoir"] = reservoir
        self.gauge.write(checkpoint)
        return True