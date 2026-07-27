from plumber.pipe import NullPipe, Pipe
from plumber.gauge import Gauge
from plumber.valve import Valve


def double(drop_in, reservoir):
    return [{"n": drop_in["n"] * 2}], reservoir


def running_total(drop_in, reservoir):
    total = reservoir.get("total", 0) + drop_in["n"]
    return [{"total": total}], {"total": total}


def make_valve(tmp_path, flow=double):
    inlet = Pipe(tmp_path, "in")
    outlet = Pipe(tmp_path, "out")
    gauge = Gauge(tmp_path, "valve")
    return Valve(flow, inlet, outlet, gauge), inlet, outlet, gauge


def test_drip_processes_one_drop_and_advances_gauge(tmp_path):
    valve, inlet, outlet, gauge = make_valve(tmp_path)
    inlet.append([{"n": 1}, {"n": 2}])

    processed = valve.drip()

    assert processed is True
    assert [d for d, _ in outlet.read_from(0)] == [{"n": 2}]
    checkpoint = gauge.read()
    assert checkpoint["read_offset"] > 0
    assert checkpoint["write_offset"] > 0


def test_drip_returns_false_when_no_new_drops(tmp_path):
    valve, inlet, outlet, gauge = make_valve(tmp_path)

    assert valve.drip() is False


def test_drip_processes_one_drop_at_a_time(tmp_path):
    valve, inlet, outlet, gauge = make_valve(tmp_path)
    inlet.append([{"n": 1}, {"n": 2}])

    valve.drip()
    valve.drip()

    assert [d for d, _ in outlet.read_from(0)] == [{"n": 2}, {"n": 4}]
    assert valve.drip() is False


def test_recovers_from_partial_write_by_reprocessing(tmp_path):
    valve, inlet, outlet, gauge = make_valve(tmp_path)
    inlet.append([{"n": 1}])

    valve.drip()

    # simulate a crash: a partial write landed in the outlet after the
    # last committed write_offset, but the gauge was never updated to match.
    with open(outlet.path, "ab") as f:
        f.write(b'{"n": incomplete')

    valve.drip()

    assert [d for d, _ in outlet.read_from(0)] == [{"n": 2}]


def test_reservoir_threads_across_drips(tmp_path):
    valve, inlet, outlet, gauge = make_valve(tmp_path, flow=running_total)
    inlet.append([{"n": 1}, {"n": 2}, {"n": 3}])

    valve.drip()
    valve.drip()
    valve.drip()

    assert [d for d, _ in outlet.read_from(0)] == [{"total": 1}, {"total": 3}, {"total": 6}]
    assert gauge.read()["reservoir"] == {"total": 6}


def counter_source(drop_in, reservoir):
    n = reservoir.get("n", 0) + 1
    return [{"n": n}], {"n": n}


def test_source_valve_fires_every_drip_with_no_inlet(tmp_path):
    outlet = Pipe(tmp_path, "out")
    gauge = Gauge(tmp_path, "valve")
    valve = Valve(counter_source, NullPipe(), outlet, gauge)

    assert valve.drip() is True
    assert valve.drip() is True
    assert valve.drip() is True

    assert [d for d, _ in outlet.read_from(0)] == [{"n": 1}, {"n": 2}, {"n": 3}]


def sink_flow(drop_in, reservoir):
    return [], reservoir


def test_sink_valve_discards_output_with_no_outlet(tmp_path):
    inlet = Pipe(tmp_path, "in")
    gauge = Gauge(tmp_path, "valve")
    valve = Valve(sink_flow, inlet, NullPipe(), gauge)
    inlet.append([{"n": 1}])

    assert valve.drip() is True
    assert valve.drip() is False

    assert gauge.read()["read_offset"] > 0


def sink_flow_with_stray_output(drop_in, reservoir):
    return [{"n": drop_in["n"]}], reservoir


def test_sink_valve_silently_discards_nonempty_output(tmp_path):
    inlet = Pipe(tmp_path, "in")
    gauge = Gauge(tmp_path, "valve")
    valve = Valve(sink_flow_with_stray_output, inlet, NullPipe(), gauge)
    inlet.append([{"n": 1}])

    assert valve.drip() is True

    assert gauge.read()["write_offset"] == 0