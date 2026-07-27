import pytest

from plumber.actuator import Actuator
from plumber.decorator import valve
from plumber.pipeline import Pipeline


def test_valid_pipeline_stores_flows_and_builds_actuators(tmp_path):
    @valve(outlet="raw")
    def watch_directory():
        return []

    @valve(inlet="raw", outlet="attached")
    def attach_metadata(d):
        return [d]

    pipeline = Pipeline([watch_directory, attach_metadata], tmp_path)

    assert pipeline.flows == [watch_directory, attach_metadata]
    assert set(pipeline.actuators) == {watch_directory.id, attach_metadata.id}
    assert all(isinstance(a, Actuator) for a in pipeline.actuators.values())


def test_two_producers_for_same_outlet_raises(tmp_path):
    @valve(outlet="raw")
    def watch_directory_a():
        return []

    @valve(outlet="raw")
    def watch_directory_b():
        return []

    with pytest.raises(ValueError, match="raw"):
        Pipeline([watch_directory_a, watch_directory_b], tmp_path)


def test_inlet_with_no_producer_raises(tmp_path):
    @valve(inlet="raw", outlet="attached")
    def attach_metadata(d):
        return [d]

    with pytest.raises(ValueError, match="raw"):
        Pipeline([attach_metadata], tmp_path)