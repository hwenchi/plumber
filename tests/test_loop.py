import pytest

from plumber.loop import run_forever


class StopTest(Exception):
    pass


class FakeValve:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    def drip(self):
        self.calls += 1
        if not self.results:
            raise StopTest
        return self.results.pop(0)


def test_run_forever_sleeps_only_when_drip_returns_false():
    valve = FakeValve([True, False, True, False, False])
    slept = []

    with pytest.raises(StopTest):
        run_forever(valve, poll_interval=0.01, sleep=slept.append)

    assert valve.calls == 6
    assert slept == [0.01, 0.01, 0.01]