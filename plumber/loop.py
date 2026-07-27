import time


def run_forever(valve, backoff=0.1, throttle=0.0, sleep=time.sleep, clock=time.monotonic):
    """Drip until killed.

    backoff waits for more data after the inlet comes up empty. throttle caps
    the drip rate, so a valve that always has work still yields.
    """
    while True:
        started = clock()
        if not valve.drip():
            sleep(backoff)
            continue

        remaining = throttle - (clock() - started)
        if remaining > 0:
            sleep(remaining)