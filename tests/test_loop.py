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


def fake_clock(readings):
    ticks = iter(readings)
    return lambda: next(ticks)


def test_backoff_sleeps_only_when_drip_returns_false():
    valve = FakeValve([True, False, True, False, False])
    slept = []

    with pytest.raises(StopTest):
        run_forever(valve, backoff=0.01, sleep=slept.append, clock=fake_clock([0.0] * 12))

    assert valve.calls == 6
    assert slept == [0.01, 0.01, 0.01]


def test_throttle_sleeps_the_remainder_of_the_interval():
    valve = FakeValve([True, True])
    slept = []
    clock = fake_clock([0.0, 0.02, 1.0, 1.005, 2.0])

    with pytest.raises(StopTest):
        run_forever(valve, backoff=0.5, throttle=0.1, sleep=slept.append, clock=clock)

    assert slept == pytest.approx([0.08, 0.095])


def test_throttle_does_not_sleep_when_the_drip_was_slower():
    valve = FakeValve([True])
    slept = []
    clock = fake_clock([0.0, 0.5, 1.0])

    with pytest.raises(StopTest):
        run_forever(valve, backoff=0.5, throttle=0.1, sleep=slept.append, clock=clock)

    assert slept == []


def test_backoff_applies_even_when_throttled():
    valve = FakeValve([False, True])
    slept = []
    clock = fake_clock([0.0, 1.0, 1.0, 2.0])

    with pytest.raises(StopTest):
        run_forever(valve, backoff=0.5, throttle=0.1, sleep=slept.append, clock=clock)

    assert slept == pytest.approx([0.5, 0.1])
