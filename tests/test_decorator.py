from plumber.decorator import valve


def test_stateless_transform_ignores_reservoir():
    @valve(inlet="raw", outlet="attached")
    def attach_metadata(d):
        return [{"camera_id": d["camera_id"]}]

    drops_out, reservoir = attach_metadata({"camera_id": "cam0"}, {"untouched": True})

    assert drops_out == [{"camera_id": "cam0"}]
    assert reservoir == {"untouched": True}


def test_valve_carries_metadata():
    @valve(inlet="raw", outlet="attached")
    def attach_metadata(d):
        return [d]

    assert attach_metadata.inlet == "raw"
    assert attach_metadata.outlet == "attached"
    assert attach_metadata.id.endswith(".attach_metadata")


def test_stateful_valve_threads_reservoir():
    @valve(inlet="inferred", outlet="stitched")
    def running_total(d, reservoir):
        total = reservoir.get("total", 0) + d["n"]
        return [{"total": total}], {"total": total}

    drops_out, reservoir = running_total({"n": 3}, {"total": 2})

    assert drops_out == [{"total": 5}]
    assert reservoir == {"total": 5}
    assert running_total.inlet == "inferred"
    assert running_total.outlet == "stitched"


def test_source_valve_takes_no_arguments():
    @valve(outlet="raw")
    def watch_directory():
        return [{"n": 1}]

    drops_out, reservoir = watch_directory(None, {"untouched": True})

    assert drops_out == [{"n": 1}]
    assert reservoir == {"untouched": True}
