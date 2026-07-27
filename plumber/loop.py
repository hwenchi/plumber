import time


def run_forever(valve, poll_interval=0.1, sleep=time.sleep):
    while True:
        if not valve.drip():
            sleep(poll_interval)
