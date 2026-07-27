from plumber.gauge import Gauge


def test_read_missing_gauge_returns_default(tmp_path):
    gauge = Gauge(tmp_path, "watch_directory")

    checkpoint = gauge.read()

    assert checkpoint == {"read_offset": 0, "write_offset": 0, "reservoir": {}}


def test_write_then_read_round_trips(tmp_path):
    gauge = Gauge(tmp_path, "attach_metadata")
    checkpoint = {"read_offset": 64, "write_offset": 128, "reservoir": {"count": 3}}

    gauge.write(checkpoint)

    assert gauge.read() == checkpoint


def test_write_leaves_no_tmp_file_behind(tmp_path):
    gauge = Gauge(tmp_path, "attach_metadata")

    gauge.write({"read_offset": 1, "write_offset": 0, "reservoir": None})

    assert not (tmp_path / "gauges" / "attach_metadata.json.tmp").exists()
    assert gauge.path.exists()